"""
RouteCipher - an educational toy cipher (NOT for protecting real data).

Settings
- Key: IP address (4 octets, each taken mod 26)
- Packet size (MTU): 4 letters
- Padding: X, added before encryption
- TTL: 2  (hop 1 = shift, hop 2 = reverse)
- Checksum: sum of letter positions mod 26
- Letters: A=0 ... Z=25
"""

MTU = 4
PAD = "X"
TTL = 2
DEFAULT_KEY = "172.16.4.9"


# ---------------------------------------------------------------- helpers
def l2n(c):
    return ord(c) - 65


def n2l(n):
    return chr(n % 26 + 65)


def validate_ip(text):
    """Return a list of 4 ints if text is a valid IP address, else None."""
    parts = text.strip().split(".")
    if len(parts) != 4:
        return None
    octets = []
    for p in parts:
        if not p.isdigit() or not p.isascii():
            return None
        n = int(p)
        if n > 255:
            return None
        octets.append(n)
    return octets


def clean_text(raw):
    """Uppercase and keep only A-Z letters."""
    return "".join(c for c in raw.upper() if "A" <= c <= "Z")


def base_shifts(octets):
    return [o % 26 for o in octets]


def split_packets(text):
    return [text[i:i + MTU] for i in range(0, len(text), MTU)]


def pad_packet(chunk):
    return chunk + PAD * (MTU - len(chunk))


def packet_shifts(base, seq):
    return [(b + seq) % 26 for b in base]


def shift_text(text, shifts, direction=1):
    return "".join(n2l(l2n(c) + direction * s) for c, s in zip(text, shifts))


def checksum(payload):
    return n2l(sum(l2n(c) for c in payload))


def shift_detail(text, shifts, direction=1):
    """Letter-by-letter explanation lines."""
    lines = []
    sign = "+" if direction == 1 else "-"
    for c, s in zip(text, shifts):
        raw = l2n(c) + direction * s
        res = n2l(raw)
        lines.append(f"    {c}({l2n(c)}) {sign} {s} = {raw} -> mod 26 = {raw % 26} = {res}")
    return lines


# ---------------------------------------------------------------- core
def encrypt(plain, octets):
    """Return a list of packets (dicts)."""
    base = base_shifts(octets)
    packets = []
    for i, chunk in enumerate(split_packets(plain), start=1):
        length = len(chunk)
        padded = pad_packet(chunk)
        hop1 = shift_text(padded, packet_shifts(base, i))
        hop2 = hop1[::-1]
        packets.append({"seq": i, "ttl": TTL, "len": length,
                        "payload": hop2, "chk": checksum(hop2)})
    return packets


def decrypt(packets, octets):
    """Return (plaintext, list of bad packet seq numbers)."""
    base = base_shifts(octets)
    out, bad = "", []
    for p in sorted(packets, key=lambda p: p["seq"]):
        if checksum(p["payload"]) != p["chk"]:
            bad.append(p["seq"])
            continue
        unrev = p["payload"][::-1]
        plain = shift_text(unrev, packet_shifts(base, p["seq"]), direction=-1)
        out += plain[:p["len"]]
    return out, bad


def print_packets(packets):
    print("  Seq | TTL | Len | Payload | Chk")
    print("  ----+-----+-----+---------+----")
    for p in packets:
        print(f"  {p['seq']:<3} | {p['ttl']:<3} | {p['len']:<3} | {p['payload']:<7} | {p['chk']}")
    print("\n  Encrypted text:", "".join(p["payload"] for p in packets))


# ---------------------------------------------------------------- input
def ask_key():
    while True:
        raw = input("Enter IP address key (e.g. 172.16.4.9): ")
        octets = validate_ip(raw)
        if octets:
            return raw.strip(), octets
        print("  Invalid IP. Use 4 numbers from 0-255 separated by dots, e.g. 192.168.10.25\n")


def ask_text():
    while True:
        raw = input("Enter plain text: ")
        text = clean_text(raw)
        if not text:
            print("  Please enter at least one letter (A-Z).\n")
            continue
        if text != raw.upper():
            print(f"  Note: only letters A-Z are used. Spaces/numbers/symbols removed -> {text}")
        return text


# ---------------------------------------------------------------- modes
def run_normal(key_str, octets, plain):
    print(f"\n  Key: {key_str}")
    print(f"  Plain text: {plain}\n")
    packets = encrypt(plain, octets)
    print_packets(packets)
    back, bad = decrypt(packets, octets)
    print(f"\n  Check - decrypting gives: {back}" + ("" if not bad else f"  (bad packets: {bad})"))


def wait(label=""):
    input(f"\n  [Press Enter to continue{label}] ")


def run_step_by_step(key_str, octets, plain):
    base = base_shifts(octets)

    print("\n=== ENCRYPTION ===")

    print("\nStep 1: Make base shifts from the key (each octet mod 26)")
    for o in octets:
        print(f"    {o} mod 26 = {o % 26}")
    print(f"  Base shifts: {base}")
    wait()

    print("\nStep 2: Split the message into packets of", MTU, "letters")
    chunks = split_packets(plain)
    print(f"  {plain}  ->  " + " | ".join(chunks))
    wait()

    print(f"\nStep 3: Pad the last packet with {PAD} up to {MTU} letters, record Len")
    padded = []
    for i, c in enumerate(chunks, start=1):
        pc = pad_packet(c)
        padded.append(pc)
        note = "(no padding needed)" if pc == c else f"(padded with {MTU - len(c)}x {PAD})"
        print(f"  Packet {i}: {c} -> {pc}   Len = {len(c)} {note}")
    wait()

    print("\nStep 4: Build each packet's shifts (base shift + Seq, mod 26)")
    all_shifts = []
    for i in range(1, len(chunks) + 1):
        sh = packet_shifts(base, i)
        all_shifts.append(sh)
        print(f"  Packet {i} (Seq {i}): {base} + {i} -> {sh}")
    wait()

    print("\nStep 5: Hop 1 - shift each letter forward")
    hop1 = []
    for i, (pc, sh) in enumerate(zip(padded, all_shifts), start=1):
        res = shift_text(pc, sh)
        hop1.append(res)
        print(f"  Packet {i}: {pc}")
        print("\n".join(shift_detail(pc, sh)))
        print(f"    => {res}")
    wait()

    print("\nStep 6: Hop 2 - reverse the letters in each packet")
    hop2 = []
    for i, h in enumerate(hop1, start=1):
        hop2.append(h[::-1])
        print(f"  Packet {i}: {h} -> {h[::-1]}")
    wait()

    print("\nStep 7: Compute checksum (sum of letter positions mod 26)")
    chks = []
    for i, h in enumerate(hop2, start=1):
        nums = [l2n(c) for c in h]
        total = sum(nums)
        chks.append(n2l(total))
        print(f"  Packet {i}: {' + '.join(map(str, nums))} = {total}, "
              f"{total} mod 26 = {total % 26} = {n2l(total)}")
    wait()

    print("\nStep 8: Final packets")
    packets = [{"seq": i, "ttl": TTL, "len": len(chunks[i - 1]),
                "payload": hop2[i - 1], "chk": chks[i - 1]}
               for i in range(1, len(chunks) + 1)]
    print_packets(packets)
    wait(" to start decryption")

    # ---------------- decryption
    print("\n=== DECRYPTION ===")

    print("\nStep 1: Verify checksums")
    for p in packets:
        calc = checksum(p["payload"])
        status = "OK" if calc == p["chk"] else "MISMATCH"
        print(f"  Packet {p['seq']}: computed {calc}, received {p['chk']} -> {status}")
    wait()

    print("\nStep 2: Sort packets by Seq")
    print("  Order:", ", ".join(str(p["seq"]) for p in sorted(packets, key=lambda p: p["seq"])))
    wait()

    print("\nStep 3: Rebuild the shifts from the key and Seq")
    for p in packets:
        print(f"  Packet {p['seq']}: {packet_shifts(base, p['seq'])}")
    wait()

    print("\nStep 4: Undo hop 2 - reverse the payload again")
    unrev = []
    for p in packets:
        r = p["payload"][::-1]
        unrev.append(r)
        print(f"  Packet {p['seq']}: {p['payload']} -> {r}")
    wait()

    print("\nStep 5: Undo hop 1 - subtract the shifts")
    unshifted = []
    for p, r in zip(packets, unrev):
        sh = packet_shifts(base, p["seq"])
        res = shift_text(r, sh, direction=-1)
        unshifted.append(res)
        print(f"  Packet {p['seq']}: {r}")
        print("\n".join(shift_detail(r, sh, direction=-1)))
        print(f"    => {res}")
    wait()

    print("\nStep 6: Remove padding using Len")
    real = []
    for p, u in zip(packets, unshifted):
        kept = u[:p["len"]]
        real.append(kept)
        print(f"  Packet {p['seq']}: {u}, Len {p['len']} -> {kept}")
    wait()

    print("\nStep 7: Join the packets in order")
    print("  " + " + ".join(real) + " = " + "".join(real))
    print("\n  Done! Original message recovered:", "".join(real))


# ---------------------------------------------------------------- main
def main():
    print("=" * 50)
    print("  RouteCipher - educational toy cipher")
    print("  (for learning only, never use for real data)")
    print("=" * 50)

    while True:
        print("\nModes:")
        print("  1 - Enter your own IP key + plain text")
        print("  2 - Enter plain text only (default key)")
        print("  3 - Like mode 1, but step by step")
        print("  q - Quit")
        choice = input("Choose a mode: ").strip().lower()

        if choice == "1":
            key_str, octets = ask_key()
            plain = ask_text()
            run_normal(key_str, octets, plain)
        elif choice == "2":
            print(f"\nUsing default key: {DEFAULT_KEY}")
            plain = ask_text()
            run_normal(DEFAULT_KEY, validate_ip(DEFAULT_KEY), plain)
        elif choice == "3":
            key_str, octets = ask_key()
            plain = ask_text()
            print(f"\n  Key: {key_str}")
            print(f"  Plain text: {plain}")
            wait(" and begin")
            run_step_by_step(key_str, octets, plain)
        elif choice in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        else:
            print("  Please choose 1, 2, 3, or q.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
