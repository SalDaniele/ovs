# Copyright (c) 2018 Nicira, Inc.
try:
    import enchant

    extra_keywords = ['ovs', 'vswitch', 'vswitchd', 'ovs-vswitchd', 'netdev',
                      'selinux', 'ovs-ctl', 'dpctl', 'ofctl', 'openvswitch',
                      'dpdk', 'hugepage', 'hugepages', 'pmd', 'upcall',
                      'vhost', 'rx', 'tx', 'vhostuser', 'openflow', 'qsort',
                      'rxq', 'txq', 'perf', 'stats', 'struct', 'int',
                      'char', 'bool', 'upcalls', 'nicira', 'bitmask', 'ipv4',
                      'ipv6', 'tcp', 'tcp4', 'tcpv4', 'udp', 'udp4', 'udpv4',
                      'icmp', 'icmp4', 'icmpv6', 'vlan', 'vxlan', 'cksum',
                      'csum', 'checksum', 'ofproto', 'numa', 'mempool',
                      'mempools', 'mbuf', 'mbufs', 'hmap', 'cmap', 'smap',
                      'dhcpv4', 'dhcp', 'dhcpv6', 'opts', 'metadata',
                      'geneve', 'mutex', 'netdev', 'netdevs', 'subtable',
                      'virtio', 'qos', 'policer', 'datapath', 'tunctl',
                      'attr', 'ethernet', 'ether', 'defrag', 'defragment',
                      'loopback', 'sflow', 'acl', 'initializer', 'recirc',
                      'xlated', 'unclosed', 'netlink', 'msec', 'usec',
                      'nsec', 'ms', 'us', 'ns', 'kilobits', 'kbps',
                      'kilobytes', 'megabytes', 'mbps', 'gigabytes', 'gbps',
                      'megabits', 'gigabits', 'pkts', 'tuple', 'miniflow',
                      'megaflow', 'conntrack', 'vlans', 'vxlans', 'arg',
                      'tpid', 'xbundle', 'xbundles', 'mbundle', 'mbundles',
                      'netflow', 'localnet', 'odp', 'pre', 'dst', 'dest',
                      'src', 'ethertype', 'cvlan', 'ips', 'msg', 'msgs',
                      'liveness', 'userspace', 'eventmask', 'datapaths',
                      'slowpath', 'fastpath', 'multicast', 'unicast',
                      'revalidation', 'namespace', 'qdisc', 'uuid', 'ofport',
                      'subnet', 'revalidation', 'revalidator', 'revalidate',
                      'l2', 'l3', 'l4', 'openssl', 'mtu', 'ifindex', 'enum',
                      'enums', 'http', 'https', 'num', 'vconn', 'vconns',
                      'conn', 'nat', 'memset', 'memcmp', 'strcmp',
                      'strcasecmp', 'tc', 'ufid', 'api', 'ofpbuf', 'ofpbufs',
                      'hashmaps', 'hashmap', 'deref', 'dereference', 'hw',
                      'prio', 'sendmmsg', 'sendmsg', 'malloc', 'free', 'alloc',
                      'pid', 'ppid', 'pgid', 'uid', 'gid', 'sid', 'utime',
                      'stime', 'cutime', 'cstime', 'vsize', 'rss', 'rsslim',
                      'whcan', 'gtime', 'eip', 'rip', 'cgtime', 'dbg', 'gw',
                      'sbrec', 'bfd', 'sizeof', 'pmds', 'nic', 'nics', 'hwol',
                      'encap', 'decap', 'tlv', 'tlvs', 'decapsulation', 'fd',
                      'cacheline', 'xlate', 'skiplist', 'idl', 'comparator',
                      'natting', 'alg', 'pasv', 'epasv', 'wildcard', 'nated',
                      'amd64', 'x86_64', 'recirculation']

    spell_check_dict = enchant.Dict("en_US")
    for kw in extra_keywords:
        spell_check_dict.add(kw)

    no_spellcheck = False
except:
    no_spellcheck = True

spellcheck_comments = False
__regex_has_comment = re.compile(r'.*(/\*|\*\s)')
__regex_has_xxx_mark = re.compile(r'.*xxx.*', re.IGNORECASE)
__regex_added_doc_rst = re.compile(
                    r'\ndiff .*Documentation/.*rst\nnew file mode')
line_length_blacklist = re.compile(
    r'\.(am|at|etc|in|m4|mk|patch|py)$|debian/rules')
leading_whitespace_blacklist = re.compile(r'\.(mk|am|at)$|debian/rules')
        print_warning("Line is %d characters long (recommended limit is 79)"
                      % len(line))
def has_comment(line):
    """Returns TRUE if the current line contains a comment or is part of
       a block comment."""
    return __regex_has_comment.match(line) is not None


def has_xxx_mark(line):
    """Returns TRUE if the current line contains 'xxx'."""
    return __regex_has_xxx_mark.match(line) is not None


def filter_comments(current_line, keep=False):
    """remove all of the c-style comments in a line"""
    STATE_NORMAL = 0
    STATE_COMMENT_SLASH = 1
    STATE_COMMENT_CONTENTS = 3
    STATE_COMMENT_END_SLASH = 4

    state = STATE_NORMAL
    sanitized_line = ''
    check_state = STATE_NORMAL
    only_whitespace = True

    if keep:
        check_state = STATE_COMMENT_CONTENTS

    for c in current_line:
        if c == '/':
            if state == STATE_NORMAL:
                state = STATE_COMMENT_SLASH
            elif state == STATE_COMMENT_SLASH:
                # This is for c++ style comments.  We will warn later
                return sanitized_line[:1]
            elif state == STATE_COMMENT_END_SLASH:
                c = ''
                state = STATE_NORMAL
        elif c == '*':
            if only_whitespace:
                # just assume this is a continuation from the previous line
                # as a comment
                state = STATE_COMMENT_END_SLASH
            elif state == STATE_COMMENT_SLASH:
                state = STATE_COMMENT_CONTENTS
                sanitized_line = sanitized_line[:-1]
            elif state == STATE_COMMENT_CONTENTS:
                state = STATE_COMMENT_END_SLASH
        elif state == STATE_COMMENT_END_SLASH:
            # Need to re-introduce the star from the previous state, since
            # it may have been clipped by the state check below.
            c = '*' + c
            state = STATE_COMMENT_CONTENTS
        elif state == STATE_COMMENT_SLASH:
            # Need to re-introduce the slash from the previous state, since
            # it may have been clipped by the state check below.
            c = '/' + c
            state = STATE_NORMAL

        if state != check_state:
            c = ''

        if not c.isspace():
            only_whitespace = False

        sanitized_line += c

    return sanitized_line


def check_comment_spelling(line):
    if no_spellcheck or not spellcheck_comments:
        return False

    comment_words = filter_comments(line, True).replace(':', ' ').split(' ')
    for word in comment_words:
        skip = False
        strword = re.subn(r'\W+', '', word)[0].replace(',', '')
        if len(strword) and not spell_check_dict.check(strword.lower()):
            if any([check_char in word
                    for check_char in ['=', '(', '-', '_', '/', '\'']]):
                skip = True

            # special case the '.'
            if '.' in word and not word.endswith('.'):
                skip = True

            # skip proper nouns and references to macros
            if strword.isupper() or (strword[0].isupper() and
                                     strword[1:].islower()):
                skip = True

            # skip words that start with numbers
            if strword.startswith(tuple('0123456789')):
                skip = True

            if not skip:
                print_warning("Check for spelling mistakes (e.g. \"%s\")"
                              % strword)
                return True

    return False


def __check_doc_is_listed(text, doctype, docdir, docfile):
    if doctype == 'rst':
        beginre = re.compile(r'\+\+\+.*{}/index.rst'.format(docdir))
        docre = re.compile(r'\n\+.*{}'.format(docfile.replace('.rst', '')))
    elif doctype == 'automake':
        beginre = re.compile(r'\+\+\+.*Documentation/automake.mk')
        docre = re.compile(r'\n\+\t{}/{}'.format(docdir, docfile))
    else:
        raise NotImplementedError("Invalid doctype: {}".format(doctype))

    res = beginre.search(text)
    if res is None:
        return True

    hunkstart = res.span()[1]
    hunkre = re.compile(r'\n(---|\+\+\+) (\S+)')
    res = hunkre.search(text[hunkstart:])
    if res is None:
        hunkend = len(text)
    else:
        hunkend = hunkstart + res.span()[0]

    hunk = text[hunkstart:hunkend]
    # find if the file is being added.
    if docre.search(hunk) is not None:
        return False

    return True


def __check_new_docs(text, doctype):
    """Check if the documentation is listed properly. If doctype is 'rst' then
       the index.rst is checked. If the doctype is 'automake' then automake.mk
       is checked. Returns TRUE if the new file is not listed."""
    failed = False
    new_docs = __regex_added_doc_rst.findall(text)
    for doc in new_docs:
        docpathname = doc.split(' ')[2]
        gitdocdir, docfile = os.path.split(docpathname.rstrip('\n'))
        if docfile == "index.rst":
            continue

        if gitdocdir.startswith('a/'):
            docdir = gitdocdir.replace('a/', '', 1)
        else:
            docdir = gitdocdir

        if __check_doc_is_listed(text, doctype, docdir, docfile):
            if doctype == 'rst':
                print_warning("New doc {} not listed in {}/index.rst".format(
                              docfile, docdir))
            elif doctype == 'automake':
                print_warning("New doc {} not listed in "
                              "Documentation/automake.mk".format(docfile))
            else:
                raise NotImplementedError("Invalid doctype: {}".format(
                                          doctype))

            failed = True

    return failed


def check_doc_docs_automake(text):
    return __check_new_docs(text, 'automake')


def check_new_docs_index(text):
    return __check_new_docs(text, 'rst')


file_checks = [
        {'regex': __regex_added_doc_rst,
         'check': check_new_docs_index},
        {'regex': __regex_added_doc_rst,
         'check': check_doc_docs_automake}
]

     'match_name': lambda x: not line_length_blacklist.search(x),
     'check': lambda x: line_length_check(x)},
     'match_name': lambda x: not leading_whitespace_blacklist.search(x),

    {'regex': '(\.c|\.h)(\.in)?$', 'match_name': None,
     'prereq': lambda x: has_comment(x),
     'check': lambda x: has_xxx_mark(x),
     'print': lambda: print_warning("Comment with 'xxx' marker")},

    {'regex': '(\.c|\.h)(\.in)?$', 'match_name': None,
     'prereq': lambda x: has_comment(x),
     'check': lambda x: check_comment_spelling(x)},
    return lambda x: regex.search(filter_comments(x)) is not None
    [re.escape(op) for op in ['%', '<<', '>>', '<=', '>=', '==', '!=',
       '[^" +(]\+[^"+;]', '[^" -(]-[^"->;]', '[^" <>=!^|+\-*/%&]=[^"=]',
       '[^* ]/[^* ]']
            if 'print' in check:
                check['print']()
def run_file_checks(text):
    """Runs the various checks for the text."""
    for check in file_checks:
        if check['regex'].search(text) is not None:
            check['check'](text)



    PARSE_STATE_HEADING = 0
    PARSE_STATE_DIFF_HEADER = 1
    PARSE_STATE_CHANGE_BODY = 2

            parse = PARSE_STATE_CHANGE_BODY
        if parse == PARSE_STATE_DIFF_HEADER:
                parse = PARSE_STATE_CHANGE_BODY
        elif parse == PARSE_STATE_HEADING:
                parse = PARSE_STATE_DIFF_HEADER
        elif parse == PARSE_STATE_CHANGE_BODY:

    run_file_checks(text)
-S|--spellcheck-comments       Check C comments for possible spelling mistakes
        optlist, args = getopt.getopt(args, 'bhlstfS',
                                       "skip-trailing-whitespace",
                                       "spellcheck-comments"])
        elif o in ("-S", "--spellcheck-comments"):
            if no_spellcheck:
                print("WARNING: The enchant library isn't availble.")
                print("         Please install python enchant.")
            else:
                spellcheck_comments = True