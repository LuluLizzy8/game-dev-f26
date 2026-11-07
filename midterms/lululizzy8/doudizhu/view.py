"""Readable table view of one seat's observation. Uses only observe() output, so it shows nothing hidden.

An observation without a "history" key (the model-obs variant, R22) renders without last actions or history.
"""


def render(obs):
    me, landlord = obs["seat"], obs["landlord"]
    history = obs.get("history")

    def who(seat):
        tags = ["landlord" if seat == landlord else "peasant"]
        if seat == me:
            tags.append("you")
        elif seat != landlord and me != landlord:
            tags.append("teammate")
        return f"seat {seat} ({', '.join(tags)})"

    last = {seat: action for seat, action in history or []}
    lines = [f"You are {who(me)}."]
    for seat in range(3):
        line = f"  {who(seat)}: {obs['cards_left'][seat]} cards"
        if history is not None:
            line += f", last action: {last.get(seat, '-')}"
        lines.append(line)
    lines.append(f"Kitty (given to the landlord, public): {obs['kitty']}")
    if obs.get("revolution"):
        lines.append("REVOLUTION: the order of 3 through 2 is reversed (3 is highest, 2 lowest); jokers stay highest.")
    if obs["status"] == "terminal":
        lines.append("The deal is over.")
    else:
        lines.append(f"Turn: {who(obs['turn'])}")
        beat = obs["to_beat"]
        lines.append(f"To beat: {beat['cards']} played by {who(beat['seat'])}" if beat
                     else "To beat: nothing, the turn player leads any combination")
    lines.append(f"Your hand: {obs['hand']}")
    if history is not None:
        lines.append("History (oldest first):")
        lines += [f"  {i}. {who(seat)}: {action}" for i, (seat, action) in enumerate(history, 1)]
        if not history:
            lines.append("  (no plays yet)")
    return "\n".join(lines)
