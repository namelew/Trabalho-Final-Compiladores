#ifndef LRPARSER_LR1_H
#define LRPARSER_LR1_H

#include "src/automata/PushDownAutomaton.h"
#include "src/common.h"
#include "src/grammar/Grammar.h"
#include "src/parser/LRParser.h"
#include "src/util/BitSet.h"

namespace gram {
class LR1Parser : public LRParser {
  public:
    explicit LR1Parser(Grammar const &g) : LRParser(g) {}

  protected:
    // Since we want constraints in labels, and we use base implementation to do
    // that for us, we should override this method.
    [[nodiscard]] bool shouldDumpConstraint() const override { return true; }

    [[nodiscard]] std::function<size_t(const StateSeed &)>
    getSeedHashFunc() const override {
        return [](StateSeed const &seed) -> std::size_t {
            size_t res = std::hash<int>()(seed.first);
            res = res * 31 + std::hash<Constraint>()(*seed.second);
            return res;
        };
    }

    [[nodiscard]] std::function<bool(const StateSeed &, const StateSeed &)>
    getSeedEqualFunc() const override {
        return [](StateSeed const &s1, StateSeed const &s2) -> bool {
            return s1.first == s2.first && *s1.second == *s2.second;
        };
    }

    [[nodiscard]] Constraint *
    resolveLocalConstraints(const Constraint *parentConstraint,
                            const Production &production,
                            int rhsIndex) override {
        auto const &symbols = gram.getAllSymbols();
        auto const &rhs = production.rightSymbols;
        Constraint constraint(symbols.size());

        bool allNullable = true;
        for (size_t i = rhsIndex + 1; allNullable && i < rhs.size(); ++i) {
            if (!symbols[rhs[i]].nullable)
                allNullable = false;
            constraint |= symbols[rhs[i]].firstSet;
        }
        if (allNullable && parentConstraint)
            constraint |= *parentConstraint;

        return newConstraint(std::move(constraint));
    }
};
} // namespace gram

#endif