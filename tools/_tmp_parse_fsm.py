import re
from pathlib import Path

path = Path(r"c:\FSM_Platform\database\dump-domain-courier-importable.sql")
text = path.read_text(encoding="utf-8", errors="ignore")

# states of interest
m = re.search(r"INSERT INTO `fsm_states` VALUES (.*?);", text, re.S)
states = {}
if m:
    for sid, name in re.findall(r"\((\d+),'([^']+)'", m.group(1)):
        states[int(sid)] = name
        if any(x in name for x in [
            "completed", "delivered", "confirmed_post2", "courier2_parcel",
            "recipient", "pickup", "client",
        ]):
            print(f"STATE {sid}: {name}")

m = re.search(r"INSERT INTO `fsm_actions` VALUES (.*?);", text, re.S)
actions = {}
if m:
    for aid, name in re.findall(r"\((\d+),'([^']+)'", m.group(1)):
        actions[int(aid)] = name
        if any(x in name for x in [
            "pickup", "confirm", "deliver", "complete", "open_cell",
            "close_cell", "recipient", "poluchatel", "courier2",
        ]):
            print(f"ACTION {aid}: {name}")

m = re.search(r"INSERT INTO `fsm_transitions` VALUES (.*?);", text, re.S)
if m:
    # typical: (id, entity_type, from_state_id, to_state_id, action_id, ...)
    rows = re.findall(
        r"\((\d+),'([^']+)',(\d+),(\d+),(\d+)",
        m.group(1),
    )
    keywords = {
        "order_parcel_confirmed_post2",
        "order_delivered_to_client",
        "order_completed",
        "order_courier2_parcel_delivered",
        "order_courier2_has_parcel",
        "order_courier2_assigned",
    }
    print("\n--- transitions involving completion / recipient pickup ---")
    for tid, et, fs, ts, aid in rows:
        fs_n = states.get(int(fs), fs)
        ts_n = states.get(int(ts), ts)
        a_n = actions.get(int(aid), aid)
        if fs_n in keywords or ts_n in keywords or any(
            k in str(a_n) for k in (
                "pickup_poluchatel", "delivered_parcel", "recipient_confirmed",
                "confirm_courier2", "open_cell", "close_cell", "pickup_order",
            )
        ):
            print(f"T{tid}: {et} {fs_n} -[{a_n}]-> {ts_n}")

# button_states
print("\n--- button_states with pickup/confirm/complete ---")
m = re.search(r"INSERT INTO `button_states` VALUES (.*?);", text, re.S)
if m:
    for row in re.findall(
        r"\((\d+),'([^']+)','([^']*)','([^']*)','([^']*)','([^']*)'\)",
        m.group(1),
    ):
        bid, btn, label, role, status, active = row
        if any(x in btn for x in ("pickup", "confirm", "complete", "open_cell", "close_cell")):
            if any(x in status for x in (
                "confirmed_post2", "delivered", "completed", "courier2",
            )) or role == "recipient":
                print(f"B{bid}: {role}.{btn} @ {status} = {active} ({label})")
