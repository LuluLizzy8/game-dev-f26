"""Readable table view of one seat's observation. Uses only observe() output, so it shows nothing hidden."""


def render(obs):
    me, landlord = obs["seat"], obs["landlord"]

    def who(seat):
        tags = ["landlord" if seat == landlord else "peasant"]
        if seat == me:
            tags.append("you")
        elif seat != landlord and me != landlord:
            tags.append("teammate")
        return f"seat {seat} ({', '.join(tags)})"

    last = {}
    for seat, action in obs["history"]:
        last[seat] = action
    lines = [f"You are {who(me)}."]
    for seat in range(3):
        lines.append(f"  {who(seat)}: {obs['cards_left'][seat]} cards, last action: {last.get(seat, '-')}")
    lines.append(f"Kitty (given to the landlord, public): {obs['kitty']}")
    if obs["status"] == "terminal":
        lines.append("The deal is over.")
    else:
        lines.append(f"Turn: {who(obs['turn'])}")
        beat = obs["to_beat"]
        lines.append(f"To beat: {beat['cards']} played by {who(beat['seat'])}" if beat
                     else "To beat: nothing, the turn player leads any combination")
    lines.append(f"Your hand: {obs['hand']}")
    lines.append("History (oldest first):")
    lines += [f"  {i}. {who(seat)}: {action}" for i, (seat, action) in enumerate(obs["history"], 1)]
    if not obs["history"]:
        lines.append("  (no plays yet)")
    return "\n".join(lines)
