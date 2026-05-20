# Diamond Factory Gujarati Slang & Glossary

Domain-specific Gujarati terms used by workers in the factory, and how they
should be translated into English. This list powers `refine_translation()`
in [ai_clients.py](ai_clients.py) — Sarvam's context-free translation often
gets these wrong; Gemini uses this glossary to fix them.

If you hear a new term workers use that gets mistranslated, add it here AND
to the prompt in `refine_translation()`.

---

## Core noun corrections

| Gujarati | Correct English | Sarvam often says (wrong) |
|---|---|---|
| હીરો (heero) | **diamond** | "hero" the person ← #1 mistake |
| મશીન | the polishing / cutting / sawing machine | machine |
| સાહેબ / સાહબ / સાહબજી | sir / boss / supervisor | sahab |
| ભાઈ | informal "brother" — usually just polite address, often skip in English | brother |
| કારીગર | artisan / skilled worker | worker |
| મિસ્તરી | workshop master / senior technician | mister |
| પાર્ટી | customer / client | "party event" |
| માલ | goods / stock (the rough diamond or batch) | "wealth" |

---

## Tools, parts, consumables (Gujarati or Gujlish)

| Gujarati | English |
|---|---|
| ડિસ્ક / ડિસ્કુ / લેપ | polishing wheel / lap |
| ડોપ / બોપ | dop (the stick that holds the diamond against the wheel) |
| તાંગ | tang / holder |
| પાવડર | diamond polishing powder / paste |
| બાથ | chemical bath |
| તાવડી | pan / sieve / tray |

---

## Manufacturing processes (workers may name them in Gujlish)

| Gujarati | English |
|---|---|
| ૪P / ફોર પી / પ્લાનિંગ | 4P (planning stage) |
| સોઇંગ / સોઈંગ | sawing |
| બ્રુટિંગ / બ્રુટ | bruting (rounding stage) |
| પોલિશ / પોલિશિંગ | polishing |
| ફેસેટિંગ / ફેસેટ | faceting |
| QC / ક્યુસી | quality control / final inspection |

---

## Defect & condition terms

| Gujarati | English | Notes |
|---|---|---|
| ક્રેક / તિરાડ / ક્રેક પડી ગયો | crack (developed a crack) | NOT "fell" or "dropped" |
| ચીપ / ચીપીંગ / ચીપાઈ ગયો | chip / chipped on edge | |
| તૂટી ગયો | broken / chipped (in diamond context) | NOT "fully shattered" |
| કાળો પડી ગયો / બળી ગયો | turned black / burned (carbon spot or polish burn) | |
| ધાર બગડી / ધાર તૂટી | edge damaged / edge broken | |
| ફેસ ખરાબ / ફેસ ગયો | facet damaged / mis-cut facet | |
| ધૂળ / ધૂળિયો | dust / dusty (foreign particles) | |
| ઇન્ક્લુઝન / દાગ / ડાઘ | inclusion / spot / blemish inside the stone | |
| ધુમ્મસ / મિલ્કી | milky / cloudy appearance | |

---

## Action verbs that get mistranslated

| Gujarati | Correct English | Wrong translation to watch for |
|---|---|---|
| ઘસવું / ઘસતા / ઘસતા ઘસતા | polishing / while polishing | "rubbing" |
| હલવાઈ ગયો (in machine context) | got STUCK / WEDGED | "halwa" / "yogurt" |
| નીકળી ગયો | popped out / came loose | "went out" |
| પડી ગયો (about a defect) | developed / appeared | "fell" |
| દઈ નાખી / બગાડી નાખી / ખોટું કરી નાખ્યું | ruined / spoiled / damaged | "gave" |
| ઊડી ગયો / ઊડ્યો | flew off / chipped off (fragment broke away) | "flew" |
| મારી નાખ્યો (about a diamond) | ruined / destroyed | literal "killed" |
| બેસાડ્યો / બેસાડી દીધો | mounted / set (into the dop) | "sat" |
| ગોઠવ્યો | positioned / aligned | "arranged" |

---

## Quality grading

| Gujarati | English |
|---|---|
| કેરેટ | carat |
| પોઇન્ટ | point (1/100 of a carat) |
| ગ્રેડ | grade |
| ક્લેરિટી | clarity |
| કટ | cut |
| VVS / VS / SI | (leave as-is) |

---

## Quantities & filler words

| Gujarati | English | Notes |
|---|---|---|
| એક નંગ / નંગ | one piece / piece | |
| બે-ત્રણ | two-three | |
| થોડું | a bit / slightly | |
| આ, પેલું, પેલો | (drop in English) | filler |

---

## Translation rules (used in prompt)

1. Only apply a correction when the Gujarati clearly supports it.
2. Keep names, IDs, numbers, and English loanwords as-is.
3. Do NOT add information that isn't in the Gujarati.
4. Return one clean, natural English sentence (or 2–3 if needed). Punctuation natural.

---

## How to add a new term

1. Edit the prompt inside `refine_translation()` in [ai_clients.py](ai_clients.py) — add the term under the right category.
2. Mirror the addition in this file so the team can see the full glossary.
3. Test with a recording of a worker using the term.
