"""
Console Based Cryptography Program 

Ciphers available:
  1. RouteCipher (group made cipher)
  2. Caesar Cipher
  3. Vigenere Cipher
  4. Columnar Transposition Cipher

Every cipher supports encryption, decryption, a step-by-step walkthrough,
and an "About" page (origin, use, pros and cons).
"""

import textwrap
# SHARED HELPERS


def wait(label=""):
    input(f"\n  [Press Enter to continue{label}] ")


def is_letter(c):
    
    return c.isascii() and c.isalpha()


def l2n(c):
    return ord(c.upper()) - 65


def n2l(n):
    return chr(n % 26 + 65)


def ask_text_any(prompt):
    while True:
        raw = input(prompt)
        if raw.strip() == "":
            print("  Error: the text can't be empty. Please type something.\n")
            continue
        return raw


def print_about(info):
    print(f"\n=== About: {info['name']} ===")
    for title, field in (("Origin", "origin"), ("Common use", "uses")):
        print(f"\n{title}:")
        print(textwrap.fill(info[field], 72, initial_indent="  ", subsequent_indent="  "))
    for title, field in (("Pros", "pros"), ("Cons", "cons")):
        print(f"\n{title}:")
        for item in info[field]:
            print(textwrap.fill(item, 72, initial_indent="  - ", subsequent_indent="    "))
    print(f"\nKey space:\n  {info['key_space']}")



# CAESAR CIPHER


CAESAR_ABOUT = {
    "name": "Caesar Cipher",
    "origin": "Named after Julius Caesar, who is said to have used a shift of 3 "
              "to protect military messages in the 1st century BC.",
    "uses": "Today it is only used for teaching and puzzles (ROT13 is a famous "
            "variant). It is not secure for real data.",
    "pros": ["Very simple to understand and do by hand.",
             "Needs only one small number as the key."],
    "cons": ["Only 25 usable keys, so brute force finds the answer instantly.",
             "Letter frequencies are preserved, so frequency analysis breaks it.",
             "The same letter always encrypts to the same letter."],
    "key_space": "A whole number from 1 to 25 (25 possible keys). "
                 "0 and 26 would leave the text unchanged.",
}


def ask_caesar_key():
    while True:
        raw = input("Enter shift key (1-25): ").strip()
        try:
            key = int(raw)
        except ValueError:
            print(f"  Error: '{raw}' is not a whole number. Enter a number from 1 to 25.\n")
            continue
        if not 1 <= key <= 25:
            print(f"  Error: {key} is outside the key space. "
                  "Choose 1-25 (0 and 26 would leave the text unchanged).\n")
            continue
        return key


def caesar_char(c, shift):
    if "A" <= c <= "Z":
        return chr((ord(c) - 65 + shift) % 26 + 65)
    if "a" <= c <= "z":
        return chr((ord(c) - 97 + shift) % 26 + 97)
    return c


def caesar_run(text, key, enc):
    shift = key if enc else -key
    return "".join(caesar_char(c, shift) for c in text)


def caesar_steps(text, key, enc):
    sign = 1 if enc else -1
    word = "ENCRYPTION" if enc else "DECRYPTION"
    print(f"\n=== CAESAR {word} (key = {key}) ===")

    alpha = "".join(chr(65 + i) for i in range(26))
    shifted = "".join(chr((i + key) % 26 + 65) for i in range(26))
    print("\nStep 1: Write the alphabet and the alphabet shifted by the key")
    print(f"  Plain : {alpha}")
    print(f"  Cipher: {shifted}")
    if enc:
        print("  To encrypt, find the letter in the Plain row and read the Cipher row.")
    else:
        print("  To decrypt, find the letter in the Cipher row and read the Plain row.")
    wait()

    print("\nStep 2: Convert each character")
    for c in text:
        if is_letter(c):
            idx = l2n(c)
            raw = idx + sign * key
            res = caesar_char(c, sign * key)
            op = "+" if enc else "-"
            wrap = "" if 0 <= raw <= 25 else f" -> wraps to {raw % 26}"
            print(f"    {c} ({idx}) {op} {key} = {raw}{wrap}  =>  {res}")
        else:
            print(f"    {c!r} is not a letter, kept as is")
    wait()

    print("\nStep 3: Join the characters")
    print("  Result:", caesar_run(text, key, enc))



# VIGENERE CIPHER


VIGENERE_ABOUT = {
    "name": "Vigenere Cipher",
    "origin": "First described by Giovan Battista Bellaso in 1553 and later "
              "wrongly credited to Blaise de Vigenere. It was nicknamed 'the "
              "unbreakable cipher' until Kasiski (1863) and Babbage showed how "
              "to break it.",
    "uses": "Used historically for diplomatic and military messages. Today it "
            "is mostly a teaching tool for polyalphabetic substitution.",
    "pros": ["The same letter can encrypt to different letters, which defeats "
             "simple frequency analysis.",
             "Much larger key space than Caesar.",
             "Still easy to do by hand."],
    "cons": ["The repeating keyword leaks patterns (Kasiski examination, index "
             "of coincidence).",
             "Short keywords are weak.",
             "If the keyword is known or guessed, everything is revealed."],
    "key_space": "A keyword of letters A-Z. A keyword of length n has 26^n "
                 "possibilities (for example 26^4 = 456,976 for 4 letters).",
}


def ask_vigenere_key():
    while True:
        raw = input("Enter keyword (letters only, e.g. LEMON): ").strip()
        if raw == "":
            print("  Error: the keyword can't be empty.\n")
            continue
        bad = sorted({c for c in raw if not is_letter(c)})
        if bad:
            shown = ", ".join(repr(c) for c in bad)
            print(f"  Error: the keyword may only contain letters A-Z (found {shown}).\n")
            continue
        return raw.upper()


def vigenere_run(text, key, enc):
    out, i = [], 0
    for c in text:
        if is_letter(c):
            shift = l2n(key[i % len(key)])
            out.append(caesar_char(c, shift if enc else -shift))
            i += 1
        else:
            out.append(c)
    return "".join(out)


def vigenere_steps(text, key, enc):
    word = "ENCRYPTION" if enc else "DECRYPTION"
    op = "+" if enc else "-"
    print(f"\n=== VIGENERE {word} (keyword = {key}) ===")

    print("\nStep 1: Turn each keyword letter into a shift (A=0 ... Z=25)")
    print("  " + ", ".join(f"{c}={l2n(c)}" for c in key))
    wait()

    print("\nStep 2: Repeat the keyword under the letters")
    print("  (non-letters are skipped and do not use up a key letter)")
    key_row, i = [], 0
    for c in text:
        if is_letter(c):
            key_row.append(key[i % len(key)])
            i += 1
        else:
            key_row.append(" ")
    label = "Text" if enc else "Cipher"
    for start in range(0, len(text), 40):
        print(f"  {label:<6}: {text[start:start + 40]}")
        print(f"  {'Key':<6}: {''.join(key_row[start:start + 40])}\n")
    wait()

    print("\nStep 3: Shift each letter by its key letter")
    for c, k in zip(text, key_row):
        if is_letter(c):
            shift = l2n(k)
            idx = l2n(c)
            raw = idx + shift if enc else idx - shift
            res = caesar_char(c, shift if enc else -shift)
            wrap = "" if 0 <= raw <= 25 else f" -> wraps to {raw % 26}"
            print(f"    {c} {op} {k}({shift}):  {idx} {op} {shift} = {raw}{wrap}  =>  {res}")
        else:
            print(f"    {c!r} is not a letter, kept as is")
    wait()

    print("\nStep 4: Join the characters")
    print("  Result:", vigenere_run(text, key, enc))



# COLUMNAR TRANSPOSITION CIPHER


TRANSPOSITION_ABOUT = {
    "name": "Columnar Transposition Cipher",
    "origin": "Transposition (rearranging letters instead of replacing them) "
              "is very old; the ancient Greek scytale is often cited as an "
              "early example. Columnar and double transposition were widely "
              "used for field messages in the World Wars.",
    "uses": "Today it is a teaching tool, and it appears as one layer inside "
            "more complex classical ciphers.",
    "pros": ["Hides the order of the message, so it can't be read directly.",
             "Combines well with a substitution cipher for more strength.",
             "Works on any characters, including spaces and punctuation."],
    "cons": ["Letter frequencies are unchanged, so an analyst can tell it is a "
             "transposition.",
             "Short keywords give few possible column orders.",
             "Vulnerable to anagramming and known-plaintext attacks."],
    "key_space": "A keyword of 2 or more letters. A keyword with n columns "
                 "gives at most n! column orders (for example 6 letters -> 720).",
}


def ask_transposition_key():
    while True:
        raw = input("Enter keyword (2+ letters, e.g. ZEBRA): ").strip()
        if raw == "":
            print("  Error: the keyword can't be empty.\n")
            continue
        bad = sorted({c for c in raw if not is_letter(c)})
        if bad:
            shown = ", ".join(repr(c) for c in bad)
            print(f"  Error: the keyword may only contain letters A-Z (found {shown}).\n")
            continue
        if len(raw) < 2:
            print("  Error: the keyword needs at least 2 letters "
                  "(a 1-column grid wouldn't change the text).\n")
            continue
        return raw.upper()


def trans_order(key):
    """Column indexes in the order they are read (alphabetical, ties left to right)."""
    return sorted(range(len(key)), key=lambda i: (key[i], i))


def trans_ranks(key):
    order = trans_order(key)
    ranks = [0] * len(key)
    for pos, col in enumerate(order, 1):
        ranks[col] = pos
    return order, ranks


def trans_lengths(total, n):
    return [total // n + (1 if j < total % n else 0) for j in range(n)]


def trans_run(text, key, enc):
    n = len(key)
    order = trans_order(key)
    if enc:
        return "".join(text[col::n] for col in order)
    lengths = trans_lengths(len(text), n)
    cols, pos = {}, 0
    for col in order:
        cols[col] = text[pos:pos + lengths[col]]
        pos += lengths[col]
    rows = -(-len(text) // n)
    return "".join(cols[j][r] for r in range(rows) for j in range(n) if r < len(cols[j]))


def vis(s):
    """Make spaces visible in diagrams."""
    return s.replace(" ", "_")


def print_grid(key, rows, ranks):
    w = len(str(len(key)))

    def line(items):
        return "    " + " ".join(f"{x:>{w}}" for x in items)

    print(line(list(key)))
    print(line(ranks))
    print("    " + "-" * (len(key) * (w + 1) - 1))
    for r in rows:
        print(line([vis(c) for c in r]))


def transposition_steps(text, key, enc):
    n = len(key)
    order, ranks = trans_ranks(key)
    word = "ENCRYPTION" if enc else "DECRYPTION"
    print(f"\n=== COLUMNAR TRANSPOSITION {word} (keyword = {key}) ===")
    print("  (spaces are shown as _ in the diagrams)")

    print("\nStep 1: Rank the keyword letters alphabetically (ties go left to right)")
    for col in range(n):
        print(f"    column {col + 1}: {key[col]} -> rank {ranks[col]}")
    wait()

    if enc:
        print(f"\nStep 2: Write the text into a grid, {n} columns wide, row by row")
        rows = [text[i:i + n] for i in range(0, len(text), n)]
        print_grid(key, rows, ranks)
        wait()

        print("\nStep 3: Read the columns from rank 1 to rank", n)
        for pos, col in enumerate(order, 1):
            print(f"    rank {pos} (column {col + 1}, {key[col]}): {vis(text[col::n])}")
        wait()

        print("\nStep 4: Join the columns")
        print("  Result:", trans_run(text, key, True))
    else:
        total = len(text)
        lengths = trans_lengths(total, n)
        print(f"\nStep 2: Work out the column lengths ({total} characters, {n} columns)")
        for col in range(n):
            print(f"    column {col + 1} ({key[col]}): {lengths[col]} characters")
        wait()

        print("\nStep 3: Cut the cipher text into columns, in rank order")
        cols, pos = {}, 0
        for rank, col in enumerate(order, 1):
            cols[col] = text[pos:pos + lengths[col]]
            pos += lengths[col]
            print(f"    rank {rank} (column {col + 1}, {key[col]}): {vis(cols[col])}")
        wait()

        print("\nStep 4: Put each column back into its place in the grid")
        nrows = -(-total // n)
        rows = ["".join(cols[j][r] for j in range(n) if r < len(cols[j])) for r in range(nrows)]
        print_grid(key, rows, ranks)
        wait()

        print("\nStep 5: Read the grid row by row")
        print("  Result:", trans_run(text, key, False))



# ROUTECIPHER (our own cipher)
# - Key: IP address (4 octets, each taken mod 26)
# - Packet size (Maximum Transmission Unit): 4 letters, padded with X before encryption
# - TTL: 2 (hop 1 = shift, hop 2 = reverse)
# - Seq number is added to every shift
# - Checksum: sum of letter positions mod 26

MTU = 4
PAD = "X"
TTL = 2
DEFAULT_KEY = "172.16.4.9"

ROUTE_ABOUT = {
    "name": "RouteCipher (our own cipher)",
    "origin": "Designed by our group for IT129. It borrows "
              "networking ideas: the message is split into numbered packets "
              "(MTU, Seq, Len), passes through hops (TTL), and carries a "
              "checksum. The secret key is written as an IP address.",
    "uses": "Educational only. It shows how nonces (Seq), padding, rounds "
            "(TTL) and integrity checks (checksum) work in a cipher.",
    "pros": ["Seq changes the shifts per packet, so the same letter encrypts "
             "differently in different packets.",
             "Padding makes every packet the same size and the Len field "
             "removes it again.",
             "The checksum detects damaged packets before decrypting.",
             "Packets can arrive out of order and still be reassembled."],
    "cons": ["Small key space (26^4 = 456,976), so brute force is quick.",
             "Known plaintext reveals the shifts, and Seq is public.",
             "The reverse hop has no secret, so it adds little security.",
             "The checksum is unkeyed and ignores letter order.",
             "Len is sent in the open, which reveals the message length."],
    "key_space": "An IP address of 4 numbers (0-255). Each is used mod 26, so "
                 "there are 26^4 = 456,976 effective keys.",
}


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
    lines = []
    sign = "+" if direction == 1 else "-"
    for c, s in zip(text, shifts):
        raw = l2n(c) + direction * s
        lines.append(f"    {c}({l2n(c)}) {sign} {s} = {raw} -> mod 26 = {raw % 26} = {n2l(raw)}")
    return lines


def route_encrypt(plain, octets):
    base = base_shifts(octets)
    packets = []
    for i, chunk in enumerate(split_packets(plain), start=1):
        padded = pad_packet(chunk)
        hop2 = shift_text(padded, packet_shifts(base, i))[::-1]
        packets.append({"seq": i, "ttl": TTL, "len": len(chunk),
                        "payload": hop2, "chk": checksum(hop2)})
    return packets


def route_decrypt(packets, octets):
    """Return (plaintext, bad_seq_list, missing_seq_list)."""
    base = base_shifts(octets)
    out, bad = "", []
    for p in sorted(packets, key=lambda p: p["seq"]):
        if checksum(p["payload"]) != p["chk"]:
            bad.append(p["seq"])
            continue
        plain = shift_text(p["payload"][::-1], packet_shifts(base, p["seq"]), -1)
        out += plain[:p["len"]]
    seqs = {p["seq"] for p in packets}
    missing = [s for s in range(1, max(seqs) + 1) if s not in seqs]
    return out, bad, missing


def print_packets(packets):
    print("  Seq | TTL | Len | Payload | Chk")
    print("  ----+-----+-----+---------+----")
    for p in packets:
        print(f"  {p['seq']:<3} | {p['ttl']:<3} | {p['len']:<3} | {p['payload']:<7} | {p['chk']}")
    print("\n  Encrypted text:", "".join(p["payload"] for p in packets))


def ask_ip_key():
    while True:
        raw = input("Enter IP address key (e.g. 172.16.4.9): ")
        octets = validate_ip(raw)
        if octets:
            return raw.strip(), octets
        parts = raw.strip().split(".")
        if len(parts) != 4:
            print(f"  Error: an IP address needs exactly 4 numbers separated by dots "
                  f"(you gave {len(parts)}).\n")
        elif any(not p.isdigit() or not p.isascii() for p in parts):
            print("  Error: each part must be a whole number with digits only, e.g. 192.168.10.25\n")
        else:
            print("  Error: each number must be between 0 and 255.\n")


def ask_route_text(prompt="Enter plain text: "):
    while True:
        raw = input(prompt)
        text = clean_text(raw)
        if not text:
            print("  Error: please enter at least one letter (A-Z).\n")
            continue
        if text != raw.upper():
            print(f"  Note: RouteCipher only uses letters A-Z. Other characters removed -> {text}")
        return text


def parse_packet(raw, used_seqs):
    """Parse "Seq | TTL | Len | Payload | Chk". Return (packet, error)."""
    f = raw.replace("|", " ").split()
    if len(f) != 5:
        return None, "Expected 5 fields: Seq | TTL | Len | Payload | Chk  (e.g. 1 | 2 | 4 | GYVE | D)"
    seq_s, ttl_s, len_s, payload, chk = f
    if not (seq_s.isdigit() and seq_s.isascii()) or int(seq_s) < 1:
        return None, f"Seq must be a whole number starting at 1 (got '{seq_s}')."
    seq = int(seq_s)
    if seq in used_seqs:
        return None, f"Seq {seq} was already entered."
    if ttl_s != str(TTL):
        return None, f"TTL must be {TTL} for this cipher (got '{ttl_s}')."
    if not (len_s.isdigit() and len_s.isascii()) or not 1 <= int(len_s) <= MTU:
        return None, f"Len must be a number from 1 to {MTU} (got '{len_s}')."
    payload, chk = payload.upper(), chk.upper()
    if len(payload) != MTU or not all("A" <= c <= "Z" for c in payload):
        return None, f"Payload must be exactly {MTU} letters A-Z (got '{payload}')."
    if len(chk) != 1 or not "A" <= chk <= "Z":
        return None, f"Chk must be a single letter A-Z (got '{chk}')."
    return {"seq": seq, "ttl": TTL, "len": int(len_s), "payload": payload, "chk": chk}, None


def ask_packets():
    print("\nEnter the packets one per line as:  Seq | TTL | Len | Payload | Chk")
    print("Example:  1 | 2 | 4 | GYVE | D")
    print("Packets can be in any order. Press Enter on an empty line when done.")
    packets = []
    while True:
        raw = input(f"  Packet {len(packets) + 1}: ").strip()
        if raw == "":
            if not packets:
                print("  Error: enter at least one packet.")
                continue
            return packets
        pkt, err = parse_packet(raw, {p["seq"] for p in packets})
        if err:
            print(f"  Error: {err}")
        else:
            packets.append(pkt)


def route_encrypt_run(key_str, octets, plain):
    print(f"\n  Key: {key_str}")
    print(f"  Plain text: {plain}\n")
    packets = route_encrypt(plain, octets)
    print_packets(packets)
    back, bad, missing = route_decrypt(packets, octets)
    print(f"\n  Check - decrypting gives: {back}")


def route_decrypt_run(key_str, octets, packets):
    print(f"\n  Key: {key_str}\n")
    print("  Checksum verification:")
    for p in sorted(packets, key=lambda p: p["seq"]):
        calc = checksum(p["payload"])
        status = "OK" if calc == p["chk"] else f"MISMATCH (computed {calc}) - discarded"
        print(f"    Packet {p['seq']}: Chk {p['chk']} -> {status}")
    text, bad, missing = route_decrypt(packets, octets)
    print(f"\n  Decrypted text: {text}")
    if bad or missing:
        print("\n  Warning: the message is incomplete.")
        if bad:
            print(f"    - Damaged packet(s) discarded: {', '.join(map(str, bad))}")
        if missing:
            print(f"    - Missing packet(s): {', '.join(map(str, missing))}")
        print("    (A wrong key can also cause checksum-valid but garbled text, "
              "since the checksum does not depend on the key.)")


def route_steps(key_str, octets, plain):
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
        res = shift_text(r, sh, -1)
        unshifted.append(res)
        print(f"  Packet {p['seq']}: {r}")
        print("\n".join(shift_detail(r, sh, -1)))
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


def route_menu():
    while True:
        print("\n--- RouteCipher (our own cipher) ---")
        print("  1 - Encrypt (your own IP key)")
        print("  2 - Encrypt (default key)")
        print("  3 - Encrypt + decrypt, step by step")
        print("  4 - Decrypt (Recommended to encrypt something first before choosing this option")
        print("  5 - About this cipher")
        print("  b - Back to cipher list")
        choice = input("Choose an option: ").strip().lower()

        if choice == "1":
            print(f"\nKey space: {ROUTE_ABOUT['key_space']}")
            key_str, octets = ask_ip_key()
            route_encrypt_run(key_str, octets, ask_route_text())
        elif choice == "2":
            print(f"\nUsing default key: {DEFAULT_KEY}")
            route_encrypt_run(DEFAULT_KEY, validate_ip(DEFAULT_KEY), ask_route_text())
        elif choice == "3":
            print(f"\nKey space: {ROUTE_ABOUT['key_space']}")
            key_str, octets = ask_ip_key()
            plain = ask_route_text()
            print(f"\n  Key: {key_str}\n  Plain text: {plain}")
            wait(" and begin")
            route_steps(key_str, octets, plain)
        elif choice == "4":
            print(f"\nKey space: {ROUTE_ABOUT['key_space']}")
            key_str, octets = ask_ip_key()
            route_decrypt_run(key_str, octets, ask_packets())
        elif choice == "5":
            print_about(ROUTE_ABOUT)
        elif choice in ("b", "back"):
            return
        else:
            print("  Error: please choose 1, 2, 3, 4, 5, or b.")



# MENUS


CLASSICS = {
    "2": {"name": "Caesar Cipher", "about": CAESAR_ABOUT, "ask_key": ask_caesar_key,
          "run": caesar_run, "steps": caesar_steps},
    "3": {"name": "Vigenere Cipher", "about": VIGENERE_ABOUT, "ask_key": ask_vigenere_key,
          "run": vigenere_run, "steps": vigenere_steps},
    "4": {"name": "Columnar Transposition Cipher", "about": TRANSPOSITION_ABOUT,
          "ask_key": ask_transposition_key, "run": trans_run, "steps": transposition_steps},
}


def classic_menu(cfg):
    while True:
        print(f"\n--- {cfg['name']} ---")
        print("  1 - Encrypt")
        print("  2 - Decrypt")
        print("  3 - Encrypt, step by step")
        print("  4 - Decrypt, step by step")
        print("  5 - About this cipher")
        print("  b - Back to cipher list")
        choice = input("Choose an option: ").strip().lower()

        if choice in ("1", "2", "3", "4"):
            enc = choice in ("1", "3")
            print(f"\nKey space: {cfg['about']['key_space']}")
            key = cfg["ask_key"]()
            text = ask_text_any("Enter plain text: " if enc else "Enter cipher text: ")
            if choice in ("1", "2"):
                label = "Cipher text" if enc else "Plain text"
                print(f"\n  {label}: {cfg['run'](text, key, enc)}")
            else:
                print(f"\n  Key: {key}\n  Input: {text}")
                wait(" and begin")
                cfg["steps"](text, key, enc)
        elif choice == "5":
            print_about(cfg["about"])
        elif choice in ("b", "back"):
            return
        else:
            print("  Error: please choose 1, 2, 3, 4, 5, or b.")


def main():
    print("=" * 54)
    print("  Console Based Cryptography Program")
  
    print("=" * 54)

    while True:
        print("\nChoose a cipher:")
        print("  1 - RouteCipher (our own, networking-inspired)")
        for k in ("2", "3", "4"):
            print(f"  {k} - {CLASSICS[k]['name']}")
        print("  q - Quit")
        choice = input("Your choice: ").strip().lower()

        if choice == "1":
            route_menu()
        elif choice in CLASSICS:
            classic_menu(CLASSICS[choice])
        elif choice in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        else:
            print("  Error: please choose 1, 2, 3, 4, or q.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
