#!/usr/bin/env bash
# Demo script for the fatigue failure risk calculator
# Run: bash demo.sh

set -e
CMD="python3 fatigue_calc.py"

# Colors
BOLD='\033[1m'
DIM='\033[2m'
RESET='\033[0m'
CYAN='\033[36m'
GREEN='\033[32m'
YELLOW='\033[33m'
MAGENTA='\033[35m'
WHITE='\033[97m'

header() {
  echo
  echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "  ${BOLD}${CYAN}$1${RESET}"
  echo -e "${BOLD}${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo
}

scenario() {
  echo -e "  ${MAGENTA}Scenario:${RESET} $1"
}

detail() {
  echo -e "  ${DIM}$1${RESET}"
}

runcmd() {
  echo -e "  ${GREEN}\$${RESET} ${WHITE}$1${RESET}"
  eval "$1"
}

insight() {
  echo -e "  ${YELLOW}→ $1${RESET}"
}

pause() {
  echo
  read -rp "  [enter to continue] " _
  clear
}

clear

header "Fatigue Failure MSD Risk Calculator"
echo -e "  This tool implements three musculoskeletal disorder risk"
echo -e "  assessment models based on ${BOLD}fatigue failure theory${RESET}"
echo -e "  developed at Auburn University."
echo
detail "Gallagher, Sesek, Schall et al."
detail "Applied to: low back, hand/wrist, and shoulder injuries"
echo
detail "The same physics that predicts metal fatigue in bridges"
detail "predicts tissue damage from repetitive work."
pause

# ---- List models ----
header "Available Models"
runcmd "$CMD --list"
pause

# ---- LiFFT: Simple case ----
header "LiFFT: Single Lifting Task"
scenario "A warehouse worker lifts 15kg boxes from a pallet"
detail "0.45m from their spine, 600 times per shift."
echo
runcmd "$CMD lifft -t 15,0.45,600"
pause

# ---- LiFFT: Multi-task ----
header "LiFFT: Multi-Task Assessment"
scenario "Same worker also does lighter picks and occasional heavy bag lifts."
echo
runcmd "$CMD lifft -t 15,0.45,600,Palletizing -t 5,0.3,300,Light_picks -t 25,0.55,80,Heavy_bags"
insight "Heavy bags are only 80 reps but dominate the damage"
insight "due to the high load (25kg) and reach distance (0.55m)."
pause

# ---- DUET: Assembly line ----
header "DUET: Assembly Line Hand/Wrist Assessment"
scenario "An electronics assembler performs three tasks at different effort levels:"
detail "Inserting connectors (easy, OMNI 3):     2000 reps/day"
detail "Tightening screws (moderate, OMNI 5):     800 reps/day"
detail "Crimping cables (hard, OMNI 8):           150 reps/day"
echo
runcmd "$CMD duet -t 3,2000,Connectors -t 5,800,Screws -t 8,150,Crimping"
insight "Even with only 150 reps, the hard crimping task"
insight "drives the majority of cumulative damage."
pause

# ---- DUET: What-if ----
header "DUET: What-If — Tool Assists"
scenario "What if we introduce power tools to reduce exertion?"
detail "Power screwdriver: OMNI 5 → 2"
detail "Powered crimper:   OMNI 8 → 4"
echo
echo -e "  ${DIM}Before:${RESET}"
runcmd "$CMD duet -t 3,2000,Connectors -t 5,800,Screws -t 8,150,Crimping"
echo -e "  ${DIM}After:${RESET}"
runcmd "$CMD duet -t 3,2000,Connectors -t 2,800,Screws_powered -t 4,150,Crimping_powered"
insight "Targeted tool assists on high-effort tasks yield"
insight "dramatic reductions in cumulative damage and risk."
pause

# ---- Shoulder: Overhead work ----
header "Shoulder Tool: Overhead Shelf Stocking"
scenario "A retail worker stocks shelves, reaching out 20in"
detail "with 3lb items, 1500 times per shift."
echo
runcmd "$CMD shoulder -t 3,20,1500,Stocking"
pause

# ---- Shoulder: Push/pull comparison ----
header "Shoulder Tool: Handling vs Push/Pull"
scenario "Compare stocking (handling) vs cart pushing (push/pull)."
detail "Handling includes arm weight in the moment calculation."
detail "Push/pull does not."
echo
echo -e "  ${DIM}Shelf stocking (handling, 3lb at 20in, 1500 reps):${RESET}"
runcmd "$CMD shoulder -t 3,20,1500,Stocking"
echo -e "  ${DIM}Cart pushing (push_pull, 10lb at 12in, 200 reps):${RESET}"
runcmd "$CMD shoulder --task-type push_pull -t 10,12,200,Cart_pushing"
insight "Different task types use different biomechanical models"
insight "for how force translates to shoulder moment."
pause

# ---- Summary ----
header "Summary"
echo -e "  ${BOLD}Three models, one framework:${RESET}"
echo -e "    ${CYAN}lifft${RESET}     Low back injury risk from lifting"
echo -e "    ${CYAN}duet${RESET}      Hand/wrist/forearm risk from repetitive exertion"
echo -e "    ${CYAN}shoulder${RESET}  Shoulder risk from reaching/handling"
echo
echo -e "  ${BOLD}Core principle:${RESET}"
echo -e "  Cumulative micro-damage from repeated loading predicts"
echo -e "  injury risk — just like metal fatigue predicts structural failure."
echo
echo -e "  ${BOLD}Practical insight:${RESET}"
echo -e "  A few high-force exertions often cause more damage than"
echo -e "  many low-force ones. Target interventions at the highest-"
echo -e "  damage tasks for the biggest risk reductions."
echo
echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
