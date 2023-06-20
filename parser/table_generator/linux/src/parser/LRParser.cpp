#include "src/parser/LRParser.h"

#include <cassert>
#include <cstddef>
#include <memory>
#include <stack>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

#include "src/automata/PushDownAutomaton.h"
#include "src/common.h"
#include "src/display/steps.h"
#include "src/grammar/Grammar.h"
#include "src/grammar/GrammarReader.h"
#include "src/util/BitSet.h"
#include "src/util/Formatter.h"
#include "src/util/TokenReader.h"

namespace gram {

void LRParser::buildKernel() {
    const auto &productionTable = gram.getProductionTable();
    const auto &symbols = gram.getAllSymbols();

    // Initialize outer dimension.
    // We want to put "S' -> S" in the last position.
    kernelLabelMap = decltype(kernelLabelMap)(productionTable.size() + 1);

    // For normal productions.
    for (size_t prodID = 0; prodID < productionTable.size(); ++prodID) {
        auto const &production = productionTable[prodID];
        const auto &rhs = production.rightSymbols;
        auto maxIndex = rhs.size();
        std::vector<const char *> labelVec(maxIndex + 1);
        // i: position of dot
        for (size_t i = 0; i <= maxIndex; ++i) {
            // Build label
            // Labels of "S -> aB": "S -> .aB", "S -> a.B", "S -> aB."
            std::string s = symbols[production.leftSymbol].name;
            s += " ->";
            size_t j = 0;
            for (; j < i; ++j) {
                s += ' ';
                s += symbols[rhs[j]].name;
            }
            s += ' ';
            s += Constants::dot;
            for (; j < rhs.size(); ++j) {
                s += ' ';
                s += symbols[rhs[j]].name;
            }
            labelVec[i] = newString(s);
        }
        kernelLabelMap[prodID] = std::move(labelVec);
    }

    // For "S' -> S".
    std::vector<const char *> augLabelVec(2);
    const auto &startName = gram.getStartSymbol().name;
    augLabelVec[0] =
        newString(startName + "' -> " + Constants::dot + " " + startName);
    augLabelVec[1] =
        newString(startName + "' -> " + startName + " " + Constants::dot);
    kernelLabelMap[productionTable.size()] = std::move(augLabelVec);

    // Build `allTermConstraint`
    auto symbolCount = static_cast<int>(symbols.size());
    auto epsilonID = gram.getEpsilonSymbol().id;
    auto cons = newConstraint(symbolCount);
    for (int i = 0; i < symbolCount; ++i) {
        if (symbols[i].type == SymbolType::TERM && i != epsilonID) {
            cons->insert(ActionID{i});
        }
    }
    allTermConstraint = cons;
}

void LRParser::buildNFA() {
    PushDownAutomaton &M = this->nfa;
    const auto &symbols = gram.getAllSymbols();
    auto const &productionTable = gram.getProductionTable();
    util::Formatter f;

    buildKernel();

    M.setDumpFlag(shouldDumpConstraint());

    auto estimatedStateCount = symbols.size() + productionTable.size() * 4;

    // Store seeds and check if a seed exists. See definition of StateSeed.
    std::unordered_map<StateSeed, std::vector<StateID>,
                       decltype(getSeedHashFunc()),
                       decltype(getSeedEqualFunc())>
        seeds(estimatedStateCount, getSeedHashFunc(), getSeedEqualFunc());

    // One state can only link to one seed, because if constraints are
    // different, LR1 should already mark sources as different states, and LR0
    // will merge them so no new state was generated.
    // State ID => iterator to `seeds`.
    std::unordered_map<StateID, decltype(seeds.begin())> epsilonLinks;

    // Mark symbols that have their productions visited
    std::stack<decltype(seeds.begin())> unvisitedSeeds;

    auto addNewDependency = [&epsilonLinks, &unvisitedSeeds,
                             &seeds](StateID state, SymbolID symbolID,
                                     Constraint *constraint) {
        StateSeed seed = std::make_pair(symbolID, constraint);
        // Find iterator
        auto result = seeds.try_emplace(seed, std::vector<StateID>());
        // Add a dependency link
        epsilonLinks.try_emplace(state, result.first);
        // Add the seed to stack if it's new
        if (result.second) {
            unvisitedSeeds.emplace(result.first);
        }
    };

    // First we need to copy all actions by order, so symbols and actions are
    // paired.
    for (auto const &symbol : symbols) {
        M.addAction(newString(symbol.name));
    }
    M.setEndOfInputAction(gram.getEndOfInputSymbol().id);
    M.setEpsilonAction(gram.getEpsilonSymbol().id);

    // Create S' (start symbol in augmented grammar) for S
    {
        auto constraints = newConstraint(symbols.size());
        constraints->insert(
            static_cast<ActionID>(gram.getEndOfInputSymbol().id));
        auto augProdID = static_cast<ProductionID>(productionTable.size());
        StateID s0 = M.addState(augProdID, 0, constraints);
        StateID s1 = M.addState(augProdID, 1, constraints);

        auto &start = gram.getStartSymbol();
        M.addTransition(s0, s1, static_cast<ActionID>(start.id));
        M.markStartState(s0);
        //        M.markFinalState(s1);
        //        this->extendedStart = s0;
        this->auxEnd = s1;

        Production augProduction{
            SymbolID{-1}, std::vector<SymbolID>{gram.getStartSymbol().id}};
        addNewDependency(
            s0, start.id,
            resolveLocalConstraints(constraints, augProduction, 0));
    }

    // Process all seeds
    while (!unvisitedSeeds.empty()) {
        auto seedIter = unvisitedSeeds.top();
        unvisitedSeeds.pop();
        for (auto productionID : symbols[seedIter->first.first].productions) {
            auto const &production = productionTable[productionID];
            auto const &rhs = production.rightSymbols;
            StateID firstStateID;
            // Add states
            auto rhsSize = static_cast<int>(rhs.size());
            for (int i = 0; i <= rhsSize; ++i) {
                StateID stateID =
                    M.addState(productionID, i, seedIter->first.second);
                if (i == 0) {
                    firstStateID = stateID;
                }
            }
            // Link these states
            for (int i = 0; i < rhsSize; ++i) {
                auto s1 = static_cast<StateID>(firstStateID + i);
                auto s2 = static_cast<StateID>(firstStateID + i + 1);
                auto const &curSymbol = symbols[rhs[i]];
                M.addTransition(s1, s2, static_cast<ActionID>(curSymbol.id));
                // Add new dependency
                if (curSymbol.type == SymbolType::NON_TERM) {
                    auto constraint = resolveLocalConstraints(
                        seedIter->first.second, production, i);
                    addNewDependency(s1, curSymbol.id, constraint);
                }
            }
            // We are in a loop. So if a symbol has multiple productions,
            // `seed->second` will store multiple start states.
            seedIter->second.push_back(firstStateID);
        }
    }

    // display(AUTOMATON, INFO, "Mark final states", &M, (void *)outFilePrefix);

    // Creating epsilon edges for each symbol
    for (const auto &link : epsilonLinks) {
        StateID from = link.first;
        for (StateID to : link.second->second) {
            M.addEpsilonTransition(from, to);
        }
    }

    display(AUTOMATON, INFO, "NFA is built", &M, (void *)"NFA");
}

void LRParser::buildDFA() {
    // Dump flag is inherited from NFA, no need to set again.
    dfa = nfa.toDFA();
    display(AUTOMATON, INFO, "DFA is built", &dfa, (void *)"DFA");
}

void LRParser::buildParseTable() {
    auto const &states = dfa.getAllStates();
    auto const &closures = dfa.getClosures();
    auto const &symbols = gram.getAllSymbols();
    auto endOfInput = static_cast<ActionID>(gram.getEndOfInputSymbol().id);
    auto stateCount = static_cast<int>(states.size());
    auto const &auxStates = dfa.getAuxStates();

    for (int i = 0; i < stateCount; ++i) {
        auto stateID = static_cast<StateID>(i);
        // "Shift" and "Goto" items
        auto const &trans = states[stateID].transitions;
        for (auto const &tran : *trans) {
            ParseAction item{symbols[tran.action].type == SymbolType::TERM
                                 ? ParseAction::SHIFT
                                 : ParseAction::GOTO,
                             tran.destination};
            addParseTableEntry(stateID, tran.action, item);
        }
        // Process "Reduce" items
        for (auto auxStateID : closures[stateID]) {
            auto const &auxState = auxStates[auxStateID];
            ProductionID prodID = auxState.productionID;
            // Skip those which cannot be reduced.
            // prodID should be valid and not refer to the pseudo production
            // "S' -> S".
            if (prodID < 0 || prodID + 1 >= (int)kernelLabelMap.size() ||
                auxState.rhsIndex + 1 != kernelLabelMap[prodID].size()) {
                continue;
            }
            for (auto actionID : *auxStates[auxStateID].constraint) {
                addParseTableEntry(stateID, actionID,
                                   ParseAction{ParseAction::REDUCE, prodID});
            }
        }
        // Process "Accept" item.
        if (closures[stateID].contains(this->auxEnd)) {
            addParseTableEntry(stateID, endOfInput,
                               ParseAction{ParseAction::SUCCESS, -1});
        }
    }

    display(PARSE_TABLE, INFO, "Parse table", this);

    // Print summary
    printf("> Summary: %zd states, %zd table cell conflicts.\n", states.size(),
           parseTableConflicts.size());
    if (!parseTableConflicts.empty()) {
        int conflictIndex = 0;
        printf("\nConflicts happen at:\n");
        for (auto const &[stateIndex, symbolID] : parseTableConflicts) {
            printf("   %3d) State %d, Symbol %s\n", ++conflictIndex, stateIndex,
                   symbols[symbolID].name.c_str());
        }
    }
}

std::string singleParseTableEntry(LRParser::ParseAction pact) {
    using Type = LRParser::ParseAction::Type;
    std::string s;
    switch (pact.type) {
    case Type::SUCCESS:
        s += "acc";
        break;
    case Type::GOTO:
        s += std::to_string(pact.dest);
        break;
    case Type::SHIFT:
        s += 's';
        s += std::to_string(pact.dest);
        break;
    case Type::REDUCE:
        s += 'r';
        s += std::to_string(pact.productionID);
        break;
    default:
        throw std::runtime_error(
            "dumpParseTableEntry(): Unknown parse action type");
    }
    return s;
}

void LRParser::addParseTableEntry(StateID state, ActionID act,
                                  ParseAction pact) {
    using std::set;
    using std::vector;
    if (parseTable.empty()) {
        parseTable = vector<vector<set<ParseAction>>>(
            dfa.getAllStates().size(),
            vector<set<ParseAction>>(gram.getAllSymbols().size()));
    }
    auto &entrySet = parseTable[state][act];
    entrySet.insert(pact);
    if (entrySet.size() > 1) {
        parseTableConflicts.emplace(state, act);
    }
    auto entry = singleParseTableEntry(pact);
    step::addTableEntry(state, act, entry.c_str());
}

std::string LRParser::dumpParseTableEntry(StateID state,
                                          ActionID action) const {
    auto const &items = parseTable.at(state).at(action);
    std::string s;
    bool commaFlag = false;
    for (auto const &item : items) {
        if (commaFlag)
            s += ',';
        commaFlag = true;
        s += singleParseTableEntry(item);
    }
    return s;
}

void LRParser::readSymbol(util::TokenReader &reader) {
    std::string s;
    if (reader.getToken(s)) {
        auto const &symbol = gram.findSymbol(s);
        if (symbol.type == SymbolType::NON_TERM) {
            throw std::runtime_error("Non-terminals as inputs are not allowed");
        }
        if (symbol.id == gram.getEpsilonSymbol().id) {
            throw std::runtime_error("Epsilon cannot be used in input");
        } else if (symbol.id == gram.getEndOfInputSymbol().id) {
            inputFlag = false;
        }
        InputQueue.push_back(symbol.id);
        step::printf("input_queue.appendleft(%d)\n", symbol.id);
    } else {
        inputFlag = false;
        auto EOI = gram.getEndOfInputSymbol().id;
        InputQueue.push_back(EOI);
        step::printf("input_queue.appendleft(%d)\n", EOI);
    }
}

// Test given stream with parsed results
bool LRParser::test(std::istream &stream) try {

    inputFlag = true;
    stateStack.clear();
    symbolStack.clear();
    InputQueue.clear();
    astNodeStack.clear();
    stateStack.push_back(dfa.getStartState());
    step::printf("state_stack.append(%d)\n", dfa.getStartState());

    // Only one of them is used
    GrammarReader grammarReader(stream);
    util::TokenReader tokenReader(stream);
    util::TokenReader &reader = launchArgs.strict ? grammarReader : tokenReader;

    if (launchArgs.exhaustInput) {
        display(LOG, INFO,
                "Please input symbols for test (Use '$' to end the input)");
        while (inputFlag) {
            readSymbol(reader);
        }
    }

    display(PARSE_STATES, INFO, "Parser states", this);
    step::section("Init Test");

    if (!launchArgs.exhaustInput) {
        display(LOG, INFO,
                "Please input symbols for test (Use '$' to end the input)");
    }

    util::Formatter f;
    int astNodeIndex = 0;

    while (true) {
        if (InputQueue.empty() && inputFlag) {
            readSymbol(reader);
        }

        if (InputQueue.empty())
            throw std::logic_error(
                "No next symbol to use, this shouldn't be possible");

        auto const &tableEntry =
            parseTable[stateStack.back()][InputQueue.front()];

        auto choices = tableEntry.size();
        if (choices <= 0) {
            step::show("Error: No viable actions for this input.");
            throw std::runtime_error(
                "No viable action in parse table for this input");
        }
        if (choices > 1) {
            step::show("Error: Action conflicts.");
            throw std::runtime_error(
                "Multiple viable choices. Cannot decide which action "
                "to take");
        }

        // Take action
        auto const &decision = *tableEntry.begin();
        switch (decision.type) {
        case ParseAction::GOTO:
            throw std::logic_error("Goto item should be processed by reduce()");
        case ParseAction::SHIFT: {
            stateStack.push_back(decision.dest);
            step::printf("state_stack.append(%d)\n", decision.dest);

            auto front = InputQueue.front();
            symbolStack.push_back(front);
            step::printf("symbol_stack.append(%d)\n", front);
            step::astAddNode(astNodeIndex,
                             getGrammar().getAllSymbols()[front].name);
            astNodeStack.push_back(astNodeIndex);
            astNodeIndex++;

            InputQueue.pop_front();
            step::printf("input_queue.pop()\n");

            if (decision.type == ParseAction::GOTO) {
                display(LOG, VERBOSE, "Apply GOTO rule");
                step::show("Apply goto rule.");
            } else {
                display(LOG, VERBOSE, "Apply SHIFT rule");
                step::show("Apply shift rule.");
            }
            break;
        }
        case ParseAction::REDUCE:
            reduce(decision.productionID, astNodeIndex++);
            display(LOG, VERBOSE,
                    f.formatView("Apply REDUCE by production: %d",
                                 decision.productionID)
                        .data());
            break;
        case ParseAction::SUCCESS:
            display(LOG, INFO, "Success");
            step::show("Success.");
            return true;
        }

        display(PARSE_STATES, INFO, "Parser states", this);
    }
} catch (std::runtime_error const &e) {
    display(LOG, ERR, e.what());
    return false;
}

// May throw errors
void LRParser::reduce(ProductionID prodID, int astNodeIndex) {
    auto const &prod = gram.getProductionTable()[prodID];
    auto bodySize = prod.rightSymbols.size();
    if (symbolStack.size() < bodySize) {
        throw std::runtime_error(
            "Stack's symbols are not enough for reduction");
    }
    if (stateStack.size() < bodySize) {
        throw std::runtime_error("Stack's states are not enough for reduction");
    }
    auto symbolStackOffset = symbolStack.size() - prod.rightSymbols.size();
    for (size_t i = 0; i < bodySize; ++i) {
        if (symbolStack[symbolStackOffset + i] != prod.rightSymbols[i]) {
            throw std::runtime_error(
                "Stack's symbols cannot fit production body for reduction");
        }
    }
    auto head = prod.leftSymbol;
    step::astAddNode(astNodeIndex, getGrammar().getAllSymbols()[head].name);

    // Pop those states by production
    for (int i = 0; i < (int)bodySize; ++i) {
        int node = astNodeStack[astNodeStack.size() - bodySize + i];
        step::astSetParent(node, astNodeIndex);
        step::printf("symbol_stack.pop()\n");
        step::printf("state_stack.pop()\n");
    }
    symbolStack.resize(symbolStack.size() - bodySize);
    stateStack.resize(stateStack.size() - bodySize);
    astNodeStack.resize(astNodeStack.size() - bodySize);

    // Used for underlining handles at the top of symbol stack.
    step::printf("reduce_hint(%zd)\n", symbolStack.size());

    symbolStack.push_back(head);
    step::printf("symbol_stack.append(%d)\n", head);

    // Process goto.
    auto const &entry = parseTable[stateStack.back()][head];
    if (entry.size() > 1) {
        step::show("Error: Goto conflicts.");
        throw std::runtime_error(
            "Multiple viable choices. Cannot decide which action "
            "to take");
    } else if (entry.empty()) {
        step::show("Error: No viable actions for this input.");
        throw std::runtime_error(
            "No viable action in parse table for this input");
    }
    auto pact = *entry.begin();
    if (pact.type != ParseAction::GOTO) {
        step::show("Error: Invalid item");
        throw std::runtime_error(
            "No viable action in parse table for this input");
    }
    auto next = pact.dest;
    stateStack.push_back(next);
    astNodeStack.push_back(astNodeIndex);
    step::printf("state_stack.append(%d)\n", next);

    std::string s = "Apply reduce rule: ";
    s += gram.dumpProduction(prodID);
    s += ".";
    step::show(s);
}

} // namespace gram