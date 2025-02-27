# Centralized Configuration
import struct
import sys
from typing import TypeVar

DEFAULT_CONFIG = {'dry_run': True, 'log_level': 'INFO', 'backup': True}

TEST_CONFIG = {'test_dir': 'test_files', 'timeout': 30, 'skip_slow': False}

DEFAULT_LOGGING_CONFIG = {'level': 'INFO', 'format': '%(asctime)s - %(levelname)s - %(message)s',
    'backup_dir': 'backups'}

PY2 = (sys.version_info[0] == 2)

PY3 = (sys.version_info[0] == 3)

PY34 = (sys.version_info[0:2] >= (3, 4))

MAXSIZE = int((1 << 63) - 1)

_32_BIT_INTERPRETER = (struct.calcsize('P') == 4)

T = TypeVar('T')

_STRING_FIELDS = {'author', 'author_email', 'description', 'description_content_type',
    'download_url', 'home_page', 'license', 'license_expression',
    'maintainer', 'maintainer_email', 'metadata_version', 'name',
    'requires_python', 'summary', 'version'}

_LIST_FIELDS = {'classifiers', 'dynamic', 'license_files', 'obsoletes', 'obsoletes_dist',
    'platforms', 'provides', 'provides_dist', 'provides_extra', 'requires',
    'requires_dist', 'requires_external', 'supported_platforms'}

_DICT_FIELDS = {'project_urls'}

_EMAIL_TO_RAW_MAPPING = {'author': 'author', 'author-email': 'author_email', 'classifier':
    'classifiers', 'description': 'description', 'description-content-type':
    'description_content_type', 'download-url': 'download_url', 'dynamic':
    'dynamic', 'home-page': 'home_page', 'keywords': 'keywords', 'license':
    'license', 'license-expression': 'license_expression', 'license-file':
    'license_files', 'maintainer': 'maintainer', 'maintainer-email':
    'maintainer_email', 'metadata-version': 'metadata_version', 'name':
    'name', 'obsoletes': 'obsoletes', 'obsoletes-dist': 'obsoletes_dist',
    'platform': 'platforms', 'project-url': 'project_urls', 'provides':
    'provides', 'provides-dist': 'provides_dist', 'provides-extra':
    'provides_extra', 'requires': 'requires', 'requires-dist':
    'requires_dist', 'requires-external': 'requires_external',
    'requires-python': 'requires_python', 'summary': 'summary',
    'supported-platform': 'supported_platforms', 'version': 'version'}

_RAW_TO_EMAIL_MAPPING = {raw: email for email, raw in _EMAIL_TO_RAW_MAPPING.items()}

_NOT_FOUND = object()

_VALID_METADATA_VERSIONS = ['1.0', '1.1', '1.2', '2.1', '2.2', '2.3', '2.4']

_REQUIRED_ATTRS = frozenset(['metadata_version', 'name', 'version'])

_VERSION_PATTERN = """
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\\.]?
            (?P<pre_l>alpha|a|beta|b|preview|pre|c|rc)
            [-_\\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\\.]?
                (?P<post_l>post|rev|r)
                [-_\\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\\.]?
            (?P<dev_l>dev)
            [-_\\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\\+(?P<local>[a-z0-9]+(?:[-_\\.][a-z0-9]+)*))?       # local version
"""

VERSION_PATTERN = """
    v?
    (?:
        (?:(?P<epoch>[0-9]+)!)?                           # epoch
        (?P<release>[0-9]+(?:\\.[0-9]+)*)                  # release segment
        (?P<pre>                                          # pre-release
            [-_\\.]?
            (?P<pre_l>(a|b|c|rc|alpha|beta|pre|preview))
            [-_\\.]?
            (?P<pre_n>[0-9]+)?
        )?
        (?P<post>                                         # post release
            (?:-(?P<post_n1>[0-9]+))
            |
            (?:
                [-_\\.]?
                (?P<post_l>post|rev|r)
                [-_\\.]?
                (?P<post_n2>[0-9]+)?
            )
        )?
        (?P<dev>                                          # dev release
            [-_\\.]?
            (?P<dev_l>dev)
            [-_\\.]?
            (?P<dev_n>[0-9]+)?
        )?
    )
    (?:\\+(?P<local>[a-z0-9]+(?:[-_\\.][a-z0-9]+)*))?       # local version
"""

EF_ARM_ABIMASK = (4278190080)

EF_ARM_ABI_VER5 = (83886080)

EF_ARM_ABI_FLOAT_HARD = (1024)

_LEGACY_MANYLINUX_MAP = {(2, 17): 'manylinux2014', (2, 12): 'manylinux2010', (2, 5): 'manylinux1'}

C32 = (1)

C64 = (2)

I386 = (3)

S390 = (22)

X8664 = (62)

VERSION = """2.20.0"""

CREATION_FLAGS = (0)

PDFDOC_ENCODABLE = frozenset(list(range(0, 23 + 1)) + list(range(32, 126 + 1)) + [8226, 8224, 
    8225, 8230, 8212, 8211, 402, 8260, 8249, 8250, 8722, 8240, 8222, 8220, 
    8221, 8216, 8217, 8218, 8482, 64257, 64258, 321, 338, 352, 376, 381, 
    305, 322, 339, 353, 382, 8364] + [728, 711, 710, 729, 733, 731, 730, 
    732] + list(range(161, 172 + 1)) + list(range(174, 255 + 1)))

OVERRIDE_WHITELIST = {'__eq__', '__hash__', '__repr__'}

BLACK = COLOR_INDEX[0]

WHITE = COLOR_INDEX[1]

BLUE = COLOR_INDEX[4]

CYAN = Color(0, 1, 1, 1)

GREEN = Color(0, 1, 0, 1)

DARKGREEN = Color(0, 0.5, 0, 1)

MAGENTA = Color(1, 0, 1, 1)

RED = Color(1, 0, 0, 1)

LTR = (1)

RTL = (2)

DEFAULT_PERMISSIONS = Permissions()

XMP_NS_DC = """http://purl.org/dc/elements/1.1/"""

XMP_NS_PDF = """http://ns.adobe.com/pdf/1.3/"""

XMP_NS_PDFA_ID = """http://www.aiim.org/pdfa/ns/id/"""

XMP_NS_PDFA_EXTENSION = """http://www.aiim.org/pdfa/ns/extension/"""

XMP_NS_PDFA_PROPERTY = """http://www.aiim.org/pdfa/ns/property#"""

XMP_NS_PDFA_SCHEMA = """http://www.aiim.org/pdfa/ns/schema#"""

XMP_NS_PDFUA_ID = """http://www.aiim.org/pdfua/ns/id/"""

XMP_NS_PDFX_ID = """http://www.npes.org/pdfx/ns/id/"""

XMP_NS_PHOTOSHOP = """http://ns.adobe.com/photoshop/1.0/"""

XMP_NS_PRISM = """http://prismstandard.org/namespaces/basic/1.0/"""

XMP_NS_PRISM2 = """http://prismstandard.org/namespaces/basic/2.0/"""

XMP_NS_PRISM3 = """http://prismstandard.org/namespaces/basic/3.0/"""

XMP_NS_RDF = """http://www.w3.org/1999/02/22-rdf-syntax-ns#"""

XMP_NS_XMP = """http://ns.adobe.com/xap/1.0/"""

XMP_NS_XMP_MM = """http://ns.adobe.com/xap/1.0/mm/"""

XMP_NS_XMP_RIGHTS = """http://ns.adobe.com/xap/1.0/rights/"""

XMP_NS_XML = """http://www.w3.org/XML/1998/namespace"""

XPACKET_BEGIN = b'<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'

XMP_EMPTY = b'<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="pikepdf">\n <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n </rdf:RDF>\n</x:xmpmeta>\n'

XPACKET_END = b'\n<?xpacket end="w"?>\n'

XMP_CONTAINERS = [XmpContainer('Alt', AltList, AltList.append), XmpContainer('Bag', set, set
    .add), XmpContainer('Seq', list, list.append)]

LANG_ALTS = frozenset([str(QName(XMP_NS_DC, 'title')), str(QName(XMP_NS_DC,
    'description')), str(QName(XMP_NS_DC, 'rights')), str(QName(
    XMP_NS_XMP_RIGHTS, 'UsageTerms'))])

XYZ = (1)

PAGE_LOCATION_ARGS = {PageLocation.XYZ: ('left', 'top', 'zoom'), PageLocation.FitH: ('top',),
    PageLocation.FitV: ('left',), PageLocation.FitR: ('left', 'bottom',
    'right', 'top'), PageLocation.FitBH: ('top',), PageLocation.FitBV: (
    'left',)}

ALL_PAGE_LOCATION_KWARGS = set(chain.from_iterable(PAGE_LOCATION_ARGS.values()))

SIMPLE_COLORSPACES = {'/DeviceRGB', '/DeviceGray', '/CalRGB', '/CalGray'}

MAIN_COLORSPACES = (SIMPLE_COLORSPACES | {'/DeviceCMYK', '/CalCMYK', '/ICCBased'})

PRINT_COLORSPACES = {'/Separation', '/DeviceN'}

COMPLEX_FILTERS = {'/DCTDecode', '/JPXDecode', '/JBIG2Decode', '/CCITTFaxDecode'}

DEFAULT_CT_RGB = (1)

DEFAULT_CT_CMYK = (0)

ABBREVS = {b'/W': b'/Width', b'/H': b'/Height', b'/BPC': b'/BitsPerComponent', b'/IM':
    b'/ImageMask', b'/CS': b'/ColorSpace', b'/F': b'/Filter', b'/DP':
    b'/DecodeParms', b'/G': b'/DeviceGray', b'/RGB': b'/DeviceRGB',
    b'/CMYK': b'/DeviceCMYK', b'/I': b'/Indexed', b'/AHx':
    b'/ASCIIHexDecode', b'/A85': b'/ASCII85Decode', b'/LZW': b'/LZWDecode',
    b'/RL': b'/RunLengthDecode', b'/CCF': b'/CCITTFaxDecode', b'/DCT':
    b'/DCTDecode'}

REVERSE_ABBREVS = {v: k for k, v in ABBREVS.items()}

VERSION_TUPLE = object

EXEMPI = _load_exempi()

ERROR_MESSAGE = {(0): 'unknown error', (-1): 'TBD', (-2): 'unavailable', (-3): 'bad object',
    (-4): 'bad parameter', (-5): 'bad value', (-6): 'assert failure', (-7):
    'enforce failure', (-8): 'unimplemented', (-9): 'internal failure', (-
    10): 'deprecated', (-11): 'external failure', (-12): 'user abort', (-13
    ): 'std exception', (-14): 'unknown exception', (-15): 'no memory', (-
    101): 'bad schema', (-102): 'bad XPath', (-103): 'bad options', (-104):
    'bad index', (-105): 'bad iter position', (-106): 'bad parse', (-107):
    'bad serialize', (-108): 'bad file format', (-109): 'no file handler',
    (-110): 'too large for JPEG', (-201): 'bad XML', (-202): 'bad RDF', (-
    203): 'bad XMP', (-204): 'empty iterator', (-205): 'bad unicode', (-206
    ): 'bad TIFF', (-207): 'bad JPEG', (-208): 'bad PSD', (-209):
    'bad PSIR', (-210): 'bad IPTC', (-211): 'bad MPEG'}

XMP_OPEN_NOOPTION = (0)

XMP_OPEN_READ = (1)

XMP_OPEN_FORUPDATE = (2)

XMP_OPEN_ONLYXMP = (4)

XMP_OPEN_CACHETNAIL = (8)

XMP_OPEN_STRICTLY = (16)

XMP_OPEN_USESMARTHANDLER = (32)

XMP_OPEN_USEPACKETSCANNING = (64)

XMP_OPEN_LIMITSCANNING = (128)

XMP_OPEN_INBACKGROUND = (268435456)

XMP_CLOSE_NOOPTION = (0)

XMP_CLOSE_SAFEUPDATE = (1)

XMP_FT_PDF = (1346651680)

XMP_FT_PS = (1347624992)

XMP_FT_EPS = (1162892064)

XMP_FT_JPEG = (1246774599)

XMP_FT_JPEG2K = (1246779424)

XMP_FT_TIFF = (1414088262)

XMP_FT_GIF = (1195984416)

XMP_FT_PNG = (1347307296)

XMP_FT_SWF = (1398228512)

XMP_FT_FLA = (1179402528)

XMP_FT_FLV = (1179407904)

XMP_FT_MOV = (1297045024)

XMP_FT_AVI = (1096173856)

XMP_FT_CIN = (1128877600)

XMP_FT_WAV = (1463899680)

XMP_FT_MP3 = (1297101600)

XMP_FT_SES = (1397052192)

XMP_FT_CEL = (1128614944)

XMP_FT_MPEG = (1297106247)

XMP_FT_MPEG2 = (1297101344)

XMP_FT_MPEG4 = (1297101856)

XMP_FT_WMAV = (1464680790)

XMP_FT_AIFF = (1095321158)

XMP_FT_HTML = (1213484364)

XMP_FT_XML = (1481460768)

XMP_FT_TEXT = (1952807028)

XMP_FT_PHOTOSHOP = (1347634208)

XMP_FT_ILLUSTRATOR = (1095311392)

XMP_FT_INDESIGN = (1229866052)

XMP_FT_AEPROJECT = (1095061536)

XMP_FT_AEPROJTEMPLATE = (1095062560)

XMP_FT_AEFILTERPRESET = (1179015200)

XMP_FT_ENCOREPROJECT = (1313034066)

XMP_FT_PREMIEREPROJECT = (1347571786)

XMP_FT_PREMIERETITLE = (1347572812)

XMP_FT_UNKNOWN = (538976288)

XMP_SERIAL_OMITPACKETWRAPPER = (16)

XMP_SERIAL_READONLYPACKET = (32)

XMP_SERIAL_USECOMPACTFORMAT = (64)

XMP_SERIAL_INCLUDETHUMBNAILPAD = (256)

XMP_SERIAL_EXACTPACKETLENGTH = (512)

XMP_SERIAL_WRITEALIASCOMMENTS = (1024)

XMP_SERIAL_OMITALLFORMATTING = (2048)

XMP_ITER_CLASSMASK = (255)

XMP_ITER_PROPERTIES = (0)

XMP_ITER_ALIASES = (1)

XMP_ITER_NAMESPACES = (2)

XMP_ITER_JUSTCHILDREN = (256)

XMP_ITER_JUSTLEAFNODES = (512)

XMP_ITER_JUSTLEAFNAME = (1024)

XMP_ITER_INCLUDEALIASES = (2048)

XMP_ITER_OMITQUALIFIERS = (4096)

XMP_ITER_SKIPSUBTREE = (1)

XMP_ITER_SKIPSIBLINGS = (2)

XMP_PROP_VALUE_IS_URI = (2)

XMP_PROP_HAS_QUALIFIERS = (16)

XMP_PROP_IS_QUALIFIER = (32)

XMP_PROP_HAS_LANG = (64)

XMP_PROP_HAS_TYPE = (128)

XMP_PROP_VALUE_IS_STRUCT = (256)

XMP_PROP_VALUE_IS_ARRAY = (512)

XMP_PROP_ARRAY_IS_UNORDERED = XMP_PROP_VALUE_IS_ARRAY

XMP_PROP_ARRAY_IS_ORDERED = (1024)

XMP_PROP_ARRAY_IS_ALT = (2048)

XMP_PROP_ARRAY_IS_ALTTEXT = (4096)

XMP_PROP_IS_ALIAS = (65536)

XMP_PROP_HAS_ALIASES = (131072)

XMP_PROP_IS_INTERNAL = (262144)

XMP_PROP_IS_STABLE = (1048576)

XMP_PROP_IS_DERIVED = (2097152)

XMP_IS_SCHEMA = (2147483648)

XMP_PROP_IS_SCHEMA = (2147483648)

XMP_PROP_ARRAY_FORM_MASK = (XMP_PROP_VALUE_IS_ARRAY | XMP_PROP_ARRAY_IS_ORDERED |
    XMP_PROP_ARRAY_IS_ALT | XMP_PROP_ARRAY_IS_ALTTEXT)

XMP_PROP_COMPOSITE_MASK = (XMP_PROP_VALUE_IS_STRUCT | XMP_PROP_ARRAY_FORM_MASK)

XMP_IMPL_RESERVED_MASK = (1879048192)

XMP_NS_XMP_BJ = """http://ns.adobe.com/xap/1.0/bj/"""

XMP_NS_EXIF = """http://ns.adobe.com/exif/1.0/"""

XMP_NS_TIFF = """http://ns.adobe.com/tiff/1.0/"""

XMP_NS_PNG = """http://ns.adobe.com/png/1.0/"""

XMP_NS_SWF = """http://ns.adobe.com/swf/1.0/"""

XMP_NS_JPEG = """http://ns.adobe.com/jpeg/1.0/"""

XMP_NS_JP2K = """http://ns.adobe.com/jp2k/1.0/"""

XMP_NS_DM = """http://ns.adobe.com/xmp/1.0/DynamicMedia/"""

XMP_NS_ASF = """http://ns.adobe.com/asf/1.0/"""

XMP_NS_WAV = """http://ns.adobe.com/xmp/wav/1.0/"""

XMP_NS_XMP_T = """http://ns.adobe.com/xap/1.0/t/"""

XMP_NS_XMP_T_PG = """http://ns.adobe.com/xap/1.0/t/pg/"""

XMP_NS_XMP_G_IMG = """http://ns.adobe.com/xap/1.0/g/img/"""

XMP_NS_DICOM = """http://ns.adobe.com/DICOM/"""

XMP_NS_PDFX = """http://ns.adobe.com/pdfx/1.3/"""

XMP_NS_CC = """http://creativecommons.org/ns#"""

XMP_NS_AVM = """http://www.communicatingastronomy.org/avm/1.0/"""

XMP_SERIAL_OPTIONS = {'omit_packet_wrapper': XMP_SERIAL_OMITPACKETWRAPPER, 'read_only_packet':
    XMP_SERIAL_READONLYPACKET, 'use_compact_format':
    XMP_SERIAL_USECOMPACTFORMAT, 'include_thumbnail_pad':
    XMP_SERIAL_INCLUDETHUMBNAILPAD, 'exact_packet_length':
    XMP_SERIAL_EXACTPACKETLENGTH, 'write_alias_comments':
    XMP_SERIAL_WRITEALIASCOMMENTS, 'omit_all_formatting':
    XMP_SERIAL_OMITALLFORMATTING}

XMP_PROP_OPTIONS = {'prop_value_is_uri': XMP_PROP_VALUE_IS_URI, 'prop_has_qualifiers':
    XMP_PROP_HAS_QUALIFIERS, 'prop_is_qualifier': XMP_PROP_IS_QUALIFIER,
    'prop_has_lang': XMP_PROP_HAS_LANG, 'prop_has_type': XMP_PROP_HAS_TYPE,
    'prop_value_is_struct': XMP_PROP_VALUE_IS_STRUCT, 'prop_value_is_array':
    XMP_PROP_VALUE_IS_ARRAY, 'prop_array_is_unordered':
    XMP_PROP_ARRAY_IS_UNORDERED, 'prop_array_is_ordered':
    XMP_PROP_ARRAY_IS_ORDERED, 'prop_array_is_alt': XMP_PROP_ARRAY_IS_ALT,
    'prop_array_is_alttext': XMP_PROP_ARRAY_IS_ALTTEXT, 'prop_is_alias':
    XMP_PROP_IS_ALIAS, 'prop_has_aliases': XMP_PROP_HAS_ALIASES,
    'prop_is_internal': XMP_PROP_IS_INTERNAL, 'prop_is_stable':
    XMP_PROP_IS_STABLE, 'prop_is_derived': XMP_PROP_IS_DERIVED,
    'prop_is_schema': XMP_PROP_IS_SCHEMA}

XMP_ITERATOR_OPTIONS = {'iter_classmask': XMP_ITER_CLASSMASK, 'iter_properties':
    XMP_ITER_PROPERTIES, 'iter_aliases': XMP_ITER_ALIASES,
    'iter_namespaces': XMP_ITER_NAMESPACES, 'iter_justchildren':
    XMP_ITER_JUSTCHILDREN, 'iter_justleafnodes': XMP_ITER_JUSTLEAFNODES,
    'iter_justleafname': XMP_ITER_JUSTLEAFNAME, 'iter_includealiases':
    XMP_ITER_INCLUDEALIASES, 'iter_omitqualifiers': XMP_ITER_OMITQUALIFIERS}

XMP_OPEN_OPTIONS = {'open_nooption': XMP_OPEN_NOOPTION, 'open_read': XMP_OPEN_READ,
    'open_forupdate': XMP_OPEN_FORUPDATE, 'open_onlyxmp': XMP_OPEN_ONLYXMP,
    'open_cachetnail': XMP_OPEN_CACHETNAIL, 'open_strictly':
    XMP_OPEN_STRICTLY, 'open_usesmarthandler': XMP_OPEN_USESMARTHANDLER,
    'open_usepacketscanning': XMP_OPEN_USEPACKETSCANNING,
    'open_limitscanning': XMP_OPEN_LIMITSCANNING, 'open_inbackground':
    XMP_OPEN_INBACKGROUND}

XMP_SKIP_OPTIONS = {'iter_skipsubtree': XMP_ITER_SKIPSUBTREE, 'iter_skipsiblings':
    XMP_ITER_SKIPSIBLINGS}

BINARIES_PATHS = []

__INIT_FILE_PATH = os.path.abspath(__file__)

DEBUG = (False)

LOADER_DIR = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))

PYTHON_EXTENSIONS_PATHS = ([LOADER_DIR] + PYTHON_EXTENSIONS_PATHS)

BASE_DIR = os.path.dirname(LOADER_DIR)

IANA_VERSION = """2024b"""

_NULL = _byte_string('\x00')

OLSON_VERSION = """2024b"""

OLSEN_VERSION = OLSON_VERSION

ZERO = timedelta(0)

HOUR = datetime.timedelta(hours=1)

UTC = tzutc()

STDOFFSET = timedelta(seconds=-_time.timezone)

DSTOFFSET = STDOFFSET

DSTDIFF = (DSTOFFSET - STDOFFSET)

DSTSTART = datetime(1, 4, 1, 2)

DSTEND = datetime(1, 10, 25, 1)

__ALL__ = ['CommaDecimalPointLocale']

ALWAYS = (True)

IF_NEEDED = (False)

NEVER = (2)

__NUMPY_SETUP__ = (False)

_VAR = re.compile('\\$\\{([a-zA-Z0-9_-]+)\\}')

_CACHE = {}

DEFAULT_NM = ['nm', '-Cs']

DEF_HEADER = ("""LIBRARY         python%s.dll
;CODE           PRELOAD MOVEABLE DISCARDABLE
;DATA           PRELOAD SINGLE

EXPORTS
"""
     % py_ver)

FUNC_RE = re.compile('^(.*) in python%s\\.dll' % py_ver, re.MULTILINE)

DATA_RE = re.compile('^_imp__(.*) in python%s\\.dll' % py_ver, re.MULTILINE)

_START = re.compile('\\[Ordinal/Name Pointer\\] Table')

_TABLE = re.compile('^\\s+\\[([\\s*[0-9]*)\\] ([a-zA-Z0-9_]*)')

_MSVCRVER_TO_FULLVER = {}

NPY_CXX_FLAGS = ['-std=c++11', '-D__STDC_VERSION__=0', '-fno-exceptions', '-fno-rtti']

GROUP_NAME = group_name.upper()

TOK = tok.upper()

HAVE_COMPILER = have_compiler()

HAS_MKL = ('mkl_rt' in mkl_info().calc_libraries_info().get('libraries', []))

TARGET_R = re.compile('Target: ([a-zA-Z0-9_\\-]*)')

IS_PYPY = ('__pypy__' in sys.builtin_module_names)

LOWER_TABLE = """""".join(_all_chars[:65] + _ascii_lower + _all_chars[65 + 26:])

UPPER_TABLE = """""".join(_all_chars[:97] + _ascii_upper + _all_chars[97 + 26:])

POSSIBLE_FLAGS = {'C': 'C', 'C_CONTIGUOUS': 'C', 'CONTIGUOUS': 'C', 'F': 'F', 'F_CONTIGUOUS':
    'F', 'FORTRAN': 'F', 'A': 'A', 'ALIGNED': 'A', 'W': 'W', 'WRITEABLE':
    'W', 'O': 'O', 'OWNDATA': 'O', 'E': 'E', 'ENSUREARRAY': 'E'}

C_ABI_VERSION = (16777225)

C_API_VERSION = (16)

FUNC_CALL_ARGS = {}

MANDATORY_FUNCS = ['sin', 'cos', 'tan', 'sinh', 'cosh', 'tanh', 'fabs', 'floor', 'ceil',
    'sqrt', 'log10', 'log', 'exp', 'asin', 'acos', 'atan', 'fmod', 'modf',
    'frexp', 'ldexp', 'expm1', 'log1p', 'acosh', 'asinh', 'atanh', 'rint',
    'trunc', 'exp2', 'copysign', 'nextafter', 'strtoll', 'strtoull', 'cbrt',
    'log2', 'pow', 'hypot', 'atan2', 'creal', 'cimag', 'conj']

OPTIONAL_LOCALE_FUNCS = ['strtold_l']

OPTIONAL_FILE_FUNCS = ['ftello', 'fseeko', 'fallocate']

OPTIONAL_MISC_FUNCS = ['backtrace', 'madvise']

OPTIONAL_VARIABLE_ATTRIBUTES = ['__thread', '__declspec(thread)']

OPTIONAL_FUNCS_MAYBE = ['ftello', 'fseeko']

C99_COMPLEX_TYPES = ['complex double', 'complex float', 'complex long double']

C99_COMPLEX_FUNCS = ['cabs', 'cacos', 'cacosh', 'carg', 'casin', 'casinh', 'catan', 'catanh',
    'cexp', 'clog', 'cpow', 'csqrt', 'csin', 'csinh', 'ccos', 'ccosh',
    'ctan', 'ctanh']

OPTIONAL_HEADERS = ['xmmintrin.h', 'emmintrin.h', 'immintrin.h', 'features.h', 'xlocale.h',
    'dlfcn.h', 'execinfo.h', 'libunwind.h', 'sys/mman.h']

OPTIONAL_INTRINSICS = [('__builtin_isnan', '5.'), ('__builtin_isinf', '5.'), (
    '__builtin_isfinite', '5.'), ('__builtin_bswap32', '5u'), (
    '__builtin_bswap64', '5u'), ('__builtin_expect', '5, 0'), (
    '__builtin_mul_overflow', '(long long)5, 5, (int*)5'), ('_m_from_int64',
    '0', 'emmintrin.h'), ('_mm_load_ps', '(float*)0', 'xmmintrin.h'), (
    '_mm_prefetch', '(float*)0, _MM_HINT_NTA', 'xmmintrin.h'), (
    '_mm_load_pd', '(double*)0', 'emmintrin.h'), ('__builtin_prefetch',
    '(float*)0, 0, 3'), ('__asm__ volatile', '"vpand %xmm1, %xmm2, %xmm3"',
    'stdio.h', 'LINK_AVX'), ('__asm__ volatile',
    '"vpand %ymm1, %ymm2, %ymm3"', 'stdio.h', 'LINK_AVX2'), (
    '__asm__ volatile', '"vpaddd %zmm1, %zmm2, %zmm3"', 'stdio.h',
    'LINK_AVX512F'), ('__asm__ volatile',
    '"vfpclasspd $0x40, %zmm15, %k6\\n"                                             "vmovdqu8 %xmm0, %xmm1\\n"                                             "vpbroadcastmb2q %k0, %xmm0\\n"'
    , 'stdio.h', 'LINK_AVX512_SKX'), ('__asm__ volatile', '"xgetbv"',
    'stdio.h', 'XGETBV')]

OPTIONAL_FUNCTION_ATTRIBUTES = [('__attribute__((optimize("unroll-loops")))',
    'attribute_optimize_unroll_loops'), ('__attribute__((optimize("O3")))',
    'attribute_optimize_opt_3'), ('__attribute__((optimize("O2")))',
    'attribute_optimize_opt_2'), ('__attribute__((nonnull (1)))',
    'attribute_nonnull')]

OPTIONAL_FUNCTION_ATTRIBUTES_AVX = [('__attribute__((target ("avx")))', 'attribute_target_avx'), (
    '__attribute__((target ("avx2")))', 'attribute_target_avx2'), (
    '__attribute__((target ("avx512f")))', 'attribute_target_avx512f'), (
    '__attribute__((target ("avx512f,avx512dq,avx512bw,avx512vl,avx512cd")))',
    'attribute_target_avx512_skx')]

OPTIONAL_FUNCTION_ATTRIBUTES_WITH_INTRINSICS_AVX = [('__attribute__((target("avx2,fma")))',
    'attribute_target_avx2_with_intrinsics',
    '__m256 temp = _mm256_set1_ps(1.0); temp =     _mm256_fmadd_ps(temp, temp, temp)'
    , 'immintrin.h'), ('__attribute__((target("avx512f")))',
    'attribute_target_avx512f_with_intrinsics',
    '__m512i temp = _mm512_castps_si512(_mm512_set1_ps(1.0))',
    'immintrin.h'), (
    '__attribute__((target ("avx512f,avx512dq,avx512bw,avx512vl,avx512cd")))',
    'attribute_target_avx512_skx_with_intrinsics',
    '__mmask8 temp = _mm512_fpclass_pd_mask(_mm512_set1_pd(1.0), 0x01);    __m512i unused_temp =         _mm512_castps_si512(_mm512_set1_ps(1.0));    _mm_mask_storeu_epi8(NULL, 0xFF, _mm_broadcastmb_epi64(temp))'
    , 'immintrin.h')]

LONG_DOUBLE_REPRESENTATION_SRC = """
/* "before" is 16 bytes to ensure there's no padding between it and "x".
 *    We're not expecting any "long double" bigger than 16 bytes or with
 *       alignment requirements stricter than 16 bytes.  */
typedef %(type)s test_type;

struct {
        char         before[16];
        test_type    x;
        char         after[8];
} foo = {
        { '\\0', '\\0', '\\0', '\\0', '\\0', '\\0', '\\0', '\\0',
          '\\001', '\\043', '\\105', '\\147', '\\211', '\\253', '\\315', '\\357' },
        -123456789.0,
        { '\\376', '\\334', '\\272', '\\230', '\\166', '\\124', '\\062', '\\020' }
};
"""

_BEFORE_SEQ = ['000', '000', '000', '000', '000', '000', '000', '000', '001', '043',
    '105', '147', '211', '253', '315', '357']

_AFTER_SEQ = ['376', '334', '272', '230', '166', '124', '062', '020']

_IEEE_DOUBLE_BE = ['301', '235', '157', '064', '124', '000', '000', '000']

_IEEE_DOUBLE_LE = _IEEE_DOUBLE_BE[::-1]

_INTEL_EXTENDED_12B = ['000', '000', '000', '000', '240', '242', '171', '353', '031', '300',
    '000', '000']

_INTEL_EXTENDED_16B = ['000', '000', '000', '000', '240', '242', '171', '353', '031', '300',
    '000', '000', '000', '000', '000', '000']

_MOTOROLA_EXTENDED_12B = ['300', '031', '000', '000', '353', '171', '242', '240', '000', '000',
    '000', '000']

_IEEE_QUAD_PREC_BE = ['300', '031', '326', '363', '105', '100', '000', '000', '000', '000',
    '000', '000', '000', '000', '000', '000']

_IEEE_QUAD_PREC_LE = _IEEE_QUAD_PREC_BE[::-1]

_IBM_DOUBLE_DOUBLE_BE = (['301', '235', '157', '064', '124', '000', '000', '000'] + ['000'] * 8)

_IBM_DOUBLE_DOUBLE_LE = (['000', '000', '000', '124', '064', '157', '235', '301'] + ['000'] * 8)

ARRAY_FUNCTION_ENABLED = bool(int(os.environ.get('NUMPY_EXPERIMENTAL_ARRAY_FUNCTION', 1)))

_MACHAR_PARAMS = {ntypes.double: dict(itype=ntypes.int64, fmt='%24.16e', title=_title_fmt.
    format('double')), ntypes.single: dict(itype=ntypes.int32, fmt='%15.7e',
    title=_title_fmt.format('single')), ntypes.longdouble: dict(itype=
    ntypes.longlong, fmt='%s', title=_title_fmt.format('long double')),
    ntypes.half: dict(itype=ntypes.int16, fmt='%12.5e', title=_title_fmt.
    format('half'))}

_KNOWN_TYPES = {}

NPY_RELAXED_STRIDES_CHECKING = (os.environ.get('NPY_RELAXED_STRIDES_CHECKING', '1') != '0')

NPY_RELAXED_STRIDES_DEBUG = (NPY_RELAXED_STRIDES_DEBUG and NPY_RELAXED_STRIDES_CHECKING)

NPY_DISABLE_SVML = (os.environ.get('NPY_DISABLE_SVML', '0') == '1')

N2 = (1)

N = (5)

NO_NEP50_WARNING = contextvars.ContextVar('_no_nep50_warning', default=False)

LOG2_STEP = (10)

STEP = (1024)

R = Point(r1, r2)

A = """A"""

_REF = {np.inf: 'inf', (-np.inf): '-inf', np.nan: 'nan'}

TESTS = {complex(np.inf, 0): '(inf+0j)', complex(0, np.inf): 'infj', complex(-np.
    inf, 0): '(-inf+0j)', complex(0, -np.inf): '-infj', complex(np.inf, 1):
    '(inf+1j)', complex(1, np.inf): '(1+infj)', complex(-np.inf, 1):
    '(-inf+1j)', complex(1, -np.inf): '(1-infj)', complex(np.nan, 0):
    '(nan+0j)', complex(0, np.nan): 'nanj', complex(-np.nan, 0): '(nan+0j)',
    complex(0, -np.nan): 'nanj', complex(np.nan, 1): '(nan+1j)', complex(1,
    np.nan): '(1+nanj)', complex(-np.nan, 1): '(nan+1j)', complex(1, -np.
    nan): '(1+nanj)'}

MAY_SHARE_BOUNDS = (0)

MAY_SHARE_EXACT = (-1)

U = E.u

X = np.arange(10 * 10, dtype='float64').reshape(10, 10)

HAVE_NOSE = (True)

PARTITION_DICT = {'partition method': np.arange(10).partition, 'argpartition method': np.
    arange(10).argpartition, 'partition function': lambda kth: np.partition
    (np.arange(10), kth), 'argpartition function': lambda kth: np.
    argpartition(np.arange(10), kth)}

UFUNCS = [obj for obj in np.core.umath.__dict__.values() if isinstance(obj, np.ufunc)]

UFUNCS_UNARY = [uf for uf in UFUNCS if uf.nin == 1]

UFUNCS_UNARY_FP = [uf for uf in UFUNCS_UNARY if 'f->f' in uf.types]

UFUNCS_BINARY = [uf for uf in UFUNCS if uf.nin == 2]

UFUNCS_BINARY_ACC = [uf for uf in UFUNCS_BINARY if hasattr(uf, 'accumulate') and uf.nout == 1]

INF_INVALID_ERR = [np.cos, np.sin, np.tan, np.arccos, np.arcsin, np.spacing, np.arctanh]

NEG_INVALID_ERR = [np.log, np.log2, np.log10, np.log1p, np.sqrt, np.arccosh, np.arctanh]

ONE_INVALID_ERR = [np.arctanh]

LTONE_INVALID_ERR = [np.arccosh]

BYZERO_ERR = [np.log, np.log2, np.log10, np.reciprocal, np.arccosh]

M = cv2.getRotationMatrix2D(center, angle, 1.0)

B = (A + np.random.default_rng(2).standard_normal(len(A)))

S = E.s

V = list(range(len(MI)))

INT64_MAX = np.iinfo(np.int64).max

INT64_MIN = np.iinfo(np.int64).min

INT64_MID = (2 ** 32)

INT128_MAX = (2 ** 128 - 1)

INT128_MIN = (-INT128_MAX)

INT128_MID = (2 ** 64)

INT64_VALUES = ([(INT64_MIN + j) for j in range(20)] + [(INT64_MAX - j) for j in range(20)
    ] + [(INT64_MID + j) for j in range(-20, 20)] + [(2 * INT64_MID + j) for
    j in range(-20, 20)] + [(INT64_MID // 2 + j) for j in range(-20, 20)] +
    list(range(-70, 70)))

INT128_VALUES = ([(INT128_MIN + j) for j in range(20)] + [(INT128_MAX - j) for j in range(
    20)] + [(INT128_MID + j) for j in range(-20, 20)] + [(2 * INT128_MID +
    j) for j in range(-20, 20)] + [(INT128_MID // 2 + j) for j in range(-20,
    20)] + list(range(-70, 70)) + [False])

INT64_POS_VALUES = [x for x in INT64_VALUES if x > 0]

SF = _get_sfloat_dtype()

C = self.data.columns[C]

A0 = self.A.decode('ascii')

P = interpolate.CubicSpline(xi, yi, axis=axis, bc_type=bc_type, extrapolate=
    extrapolate)

AB = np.array([['abcefg', '123456'], ['789051', 'xyztuv']]).view(np.chararray)

QA = np.array([['qabc', 'q123'], ['q789', 'qxyz']]).view(np.chararray)

F = TypeVar('F', bound=FuncType)

FC = np.array([['3', '7.000000'], ['19', '1']]).view(np.chararray)

A1 = f"""{self.username}:{realm}:{self.password}"""

A2 = f"""{method}:{path}"""

CAST_TABLE = _get_cancast_table()

UNARY_UFUNCS = [obj for obj in np.core.umath.__dict__.values() if isinstance(obj, np.ufunc)]

UNARY_OBJECT_UFUNCS = [uf for uf in UNARY_UFUNCS if 'O->O' in uf.types]

L = list(iterable)

S0 = np.dtype('S0')

IS_AVX = (__cpu_features__.get('AVX512F', False) or __cpu_features__.get('FMA3', 
    False) and __cpu_features__.get('AVX2', False))

COMPARISONS = [(operator.eq, np.equal, '=='), (operator.ne, np.not_equal, '!='), (
    operator.lt, np.less, '<'), (operator.le, np.less_equal, '<='), (
    operator.gt, np.greater, '>'), (operator.ge, np.greater_equal, '>=')]

S2 = np.dtype((bytes, 2))

S3 = np.dtype((bytes, 3))

S5 = np.dtype((bytes, 5))

U2 = np.dtype((str, 2))

U3 = np.dtype((str, 3))

U5 = np.dtype((str, 5))

LD_INFO = np.finfo(np.longdouble)

HANDLED_FUNCTIONS = {}

DATA = """id	num	
1	1.2 	
1	 2.1	
2	 1	
2	 1.2 	
"""

M1 = f(random_ints(), random_ints())

M2 = f(random_ints(), random_ints())

M3 = self.matmul(M1, M2)

NEIGH_MODE = {'zero': 0, 'one': 1, 'constant': 2, 'circular': 3, 'mirror': 4}

UPLO = UPLO.upper()

CASES = []

TEST_CASES = CASES

I = E.i

XERBLA_OK = (255)

D = TypeVar('D')

G = (np.random.randn(size, size) + 1.0j * np.random.randn(size, size))

XX = x.reshape(3, 2, 2, 3)

Z = (100 * X_orig.iloc[:, 1:-1].copy())

_T = TypeVar('_T')

_GENERIC_ALIAS_TYPE = (_GenericAlias,)

_SCT = TypeVar('_SCT', bound=np.generic)

PUBLIC_MODULES = [('numpy.' + s) for s in ['array_api', 'array_api.linalg', 'ctypeslib',
    'distutils', 'distutils.cpuinfo', 'distutils.exec_command',
    'distutils.misc_util', 'distutils.log', 'distutils.system_info', 'doc',
    'doc.constants', 'doc.ufuncs', 'f2py', 'fft', 'lib', 'lib.format',
    'lib.mixins', 'lib.recfunctions', 'lib.scimath', 'lib.stride_tricks',
    'linalg', 'ma', 'ma.extras', 'ma.mrecords', 'matlib', 'polynomial',
    'polynomial.chebyshev', 'polynomial.hermite', 'polynomial.hermite_e',
    'polynomial.laguerre', 'polynomial.legendre', 'polynomial.polynomial',
    'random', 'testing', 'typing', 'typing.mypy_plugin', 'version']]

PUBLIC_ALIASED_MODULES = ['numpy.char', 'numpy.emath', 'numpy.rec']

PRIVATE_BUT_PRESENT_MODULES = [('numpy.' + s) for s in ['compat', 'compat.py3k', 'conftest', 'core',
    'core.arrayprint', 'core.defchararray', 'core.einsumfunc',
    'core.fromnumeric', 'core.function_base', 'core.getlimits',
    'core.memmap', 'core.multiarray', 'core.numeric', 'core.numerictypes',
    'core.overrides', 'core.records', 'core.shape_base', 'core.umath',
    'core.umath_tests', 'distutils.armccompiler', 'distutils.ccompiler',
    'distutils.ccompiler_opt', 'distutils.command',
    'distutils.command.autodist', 'distutils.command.bdist_rpm',
    'distutils.command.build', 'distutils.command.build_clib',
    'distutils.command.build_ext', 'distutils.command.build_py',
    'distutils.command.build_scripts', 'distutils.command.build_src',
    'distutils.command.config', 'distutils.command.config_compiler',
    'distutils.command.develop', 'distutils.command.egg_info',
    'distutils.command.install', 'distutils.command.install_clib',
    'distutils.command.install_data', 'distutils.command.install_headers',
    'distutils.command.sdist', 'distutils.conv_template', 'distutils.core',
    'distutils.extension', 'distutils.fcompiler',
    'distutils.fcompiler.absoft', 'distutils.fcompiler.arm',
    'distutils.fcompiler.compaq', 'distutils.fcompiler.environment',
    'distutils.fcompiler.g95', 'distutils.fcompiler.gnu',
    'distutils.fcompiler.hpux', 'distutils.fcompiler.ibm',
    'distutils.fcompiler.intel', 'distutils.fcompiler.lahey',
    'distutils.fcompiler.mips', 'distutils.fcompiler.nag',
    'distutils.fcompiler.none', 'distutils.fcompiler.pathf95',
    'distutils.fcompiler.pg', 'distutils.fcompiler.nv',
    'distutils.fcompiler.sun', 'distutils.fcompiler.vast',
    'distutils.fcompiler.fujitsu', 'distutils.from_template',
    'distutils.intelccompiler', 'distutils.lib2def',
    'distutils.line_endings', 'distutils.mingw32ccompiler',
    'distutils.msvccompiler', 'distutils.npy_pkg_config',
    'distutils.numpy_distribution', 'distutils.pathccompiler',
    'distutils.unixccompiler', 'dual', 'f2py.auxfuncs', 'f2py.capi_maps',
    'f2py.cb_rules', 'f2py.cfuncs', 'f2py.common_rules',
    'f2py.crackfortran', 'f2py.diagnose', 'f2py.f2py2e',
    'f2py.f90mod_rules', 'f2py.func2subr', 'f2py.rules', 'f2py.symbolic',
    'f2py.use_rules', 'fft.helper', 'lib.arraypad', 'lib.arraysetops',
    'lib.arrayterator', 'lib.function_base', 'lib.histograms',
    'lib.index_tricks', 'lib.nanfunctions', 'lib.npyio', 'lib.polynomial',
    'lib.shape_base', 'lib.twodim_base', 'lib.type_check', 'lib.ufunclike',
    'lib.user_array', 'lib.utils', 'linalg.lapack_lite', 'linalg.linalg',
    'ma.bench', 'ma.core', 'ma.testutils', 'ma.timer_comparison',
    'matrixlib', 'matrixlib.defmatrix', 'polynomial.polyutils',
    'random.mtrand', 'random.bit_generator',
    'testing.print_coercion_tables', 'testing.utils']]

SKIP_LIST = ['numpy.core.code_generators', 'numpy.core.code_generators.genapi',
    'numpy.core.code_generators.generate_umath',
    'numpy.core.code_generators.ufunc_docstrings',
    'numpy.core.code_generators.generate_numpy_api',
    'numpy.core.code_generators.generate_ufunc_api',
    'numpy.core.code_generators.numpy_api',
    'numpy.core.code_generators.generate_umath_doc', 'numpy.core.cversions',
    'numpy.core.generate_numpy_api', 'numpy.distutils.msvc9compiler']

SKIP_LIST_2 = ['numpy.math', 'numpy.distutils.log.sys', 'numpy.distutils.log.logging',
    'numpy.distutils.log.warnings', 'numpy.doc.constants.re',
    'numpy.doc.constants.textwrap', 'numpy.lib.emath', 'numpy.lib.math',
    'numpy.matlib.char', 'numpy.matlib.rec', 'numpy.matlib.emath',
    'numpy.matlib.math', 'numpy.matlib.linalg', 'numpy.matlib.fft',
    'numpy.matlib.random', 'numpy.matlib.ctypeslib', 'numpy.matlib.ma']

MYPY_EX = ex

ROOT = Path(np.__file__).parents[0]

FILES = {**TestOverallBehaviour.EXAMPLES['flat-layout'], 'setup.py': dedent(
    """            import pathlib
            from setuptools import setup
            from setuptools.command.build_py import build_py as orig

            class my_build_py(orig):
                def run(self):
                    super().run()
                    raise ValueError("TEST_RAISE")

            setup(cmdclass={"build_py": my_build_py})
            """
    )}

NO_MYPY = (False)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

PASS_DIR = os.path.join(DATA_DIR, 'pass')

FAIL_DIR = os.path.join(DATA_DIR, 'fail')

REVEAL_DIR = os.path.join(DATA_DIR, 'reveal')

MISC_DIR = os.path.join(DATA_DIR, 'misc')

MYPY_INI = os.path.join(DATA_DIR, 'mypy.ini')

CACHE_DIR = os.path.join(DATA_DIR, '.mypy_cache')

_FAIL_MSG1 = """Extra error at line {}

Expression: {}
Extra error: {!r}
"""

_FAIL_MSG2 = """Error mismatch at line {}

Expression: {}
Expected error: {!r}
Observed error: {!r}
"""

_REVEAL_MSG = """Reveal mismatch at line {}

Expression: {}
Expected reveal: {!r}
Observed reveal: {!r}
"""

_STRIP_PATTERN = re.compile('(\\w+\\.)+(\\w+)')

LINENO_MAPPING = {(3): 'uint128', (4): 'uint256', (6): 'int128', (7): 'int256', (9):
    'float80', (10): 'float96', (11): 'float128', (12): 'float256', (14):
    'complex160', (15): 'complex192', (16): 'complex256', (17): 'complex512'}

TYPES = (Option.TYPES + ('path', 'package_name'))

T1 = [0, 1]

T2 = [-1, 0, 2]

GETATTR_NAMES = sorted(set(dir(np.ndarray)) - _GenericAlias._ATTR_EXCEPTIONS)

BUFFER = np.array([1], dtype=np.int64)

GE_398 = (sys.version_info[:2] == (3, 9) and sys.version_info >= (3, 9, 8))

AR_LIKE_M = [np.datetime64(1, 'D')]

AR_LIKE_O = [Object(), Object(), Object()]

AR = np.array([0, 1, 2], dtype=np.int32)

KACF = frozenset({None, 'K', 'A', 'C', 'F'})

ACF = frozenset({None, 'A', 'C', 'F'})

CF = frozenset({None, 'C', 'F'})

SEQ = (0, 1, 2, 3, 4)

B0 = np.empty((), dtype=np.int32).view(SubClass)

B1 = np.empty((1,), dtype=np.int32).view(SubClass)

B2 = np.empty((1, 1), dtype=np.int32).view(SubClass)

SEED_NONE = None

SEED_INT = (4579435749574957634658964293569)

AR_LIKE_U = ['1', '2', '3']

FILE = StringIO()

AR2 = np.array([1], dtype=np.timedelta64)

F_FUNC = """F_FUNC"""

INTEGER = (10)

REAL = (12)

COMPLEX = (8)

STRING = """u"""

ARRAY = """ARRAY"""

SYMBOL = (40)

TERNARY = (13)

APPLY = (200)

INDEXING = (210)

CONCAT = (220)

RELATIONAL = (300)

TERMS = (1000)

FACTORS = (2000)

REF = (3000)

DEREF = (3001)

EQ = (7)

NE = (2)

LT = (6)

LE = (4)

GT = (5)

GE = (6)

POS = (1)

NEG = (2)

ADD = (3)

SUB = E.sub

MUL = (5)

DIV = E.div

POW = (7)

ATOM = (0)

POWER = (1)

UNARY = (2)

PRODUCT = (3)

SUM = (4)

LAND = (11)

LOR = (12)

ASSIGN = (14)

TUPLE = (15)

NONE = (0)

COUNTER = _counter()

IS_S390X = (platform.machine() == 's390x')

MNAME = """hi"""

IS_WASM = (platform.machine() in ['wasm32', 'wasm64'])

IS_PYSTON = hasattr(sys, 'pyston_version_info')

HAS_REFCOUNT = (getattr(sys, 'getrefcount', None) is not None and not IS_PYSTON)

HAS_LAPACK64 = numpy.linalg.lapack_lite._ilp64

_OLD_PROMOTION = (lambda : np._get_promotion_state() == 'legacy')

BLOCK = (65536)

EXPECTED_KEYS = {'descr', 'fortran_order', 'shape'}

MAGIC_PREFIX = b'\x93NUMPY'

MAGIC_LEN = (len(MAGIC_PREFIX) + 2)

ARRAY_ALIGN = (64)

BUFFER_SIZE = (2 ** 18)

GROWTH_AXIS_MAX_DIGITS = (21)

_MAX_HEADER_SIZE = (10000)

_ZIP_PREFIX = b'PK\x03\x04'

_ZIP_SUFFIX = b'PK\x05\x06'

_DIMENSION_NAME = """\\w+"""

_CORE_DIMENSION_LIST = """(?:{0:}(?:,{0:})*)?""".format(_DIMENSION_NAME)

_ARGUMENT = """\\({}\\)""".format(_CORE_DIMENSION_LIST)

_ARGUMENT_LIST = """{0:}(?:,{0:})*""".format(_ARGUMENT)

_SIGNATURE = """^{0:}->{0:}$""".format(_ARGUMENT_LIST)

X_T = (X * w).T

DATA_AXIS = (0)

H = int(round(hue))

TYPE_CODES = (np.typecodes['AllInteger'] + np.typecodes['AllFloat'] + 'O')

IS_64BIT = (sys.maxsize > 2 ** 32)

HAS_BZ2 = (False)

HAS_LZMA = (False)

Y = np.ones((10, 1), dtype=int)

H_F_TYPE_CODES = ([(int_type, np.float64) for int_type in np.typecodes['AllInteger']] + [(np
    .float16, np.float16), (np.float32, np.float32), (np.float64, np.
    float64), (np.longdouble, np.longdouble), (np.complex64, np.complex64),
    (np.complex128, np.complex128), (np.clongdouble, np.clongdouble), (np.
    dtype('O'), np.float64)])

_HANDLED_TYPES = (decimal.Decimal, numbers.Number, np.ndarray)

_ALL_BINARY_OPERATORS = [operator.lt, operator.le, operator.eq, operator.ne, operator.gt, operator.
    ge, operator.add, operator.sub, operator.mul, operator.truediv,
    operator.floordiv, operator.mod, divmod, pow, operator.lshift, operator
    .rshift, operator.and_, operator.xor, operator.or_]

NANFUNCS = {np.nanmin: np.amin, np.nanmax: np.amax, np.nanargmin: np.argmin, np.
    nanargmax: np.argmax, np.nansum: np.sum, np.nanprod: np.prod, np.
    nancumsum: np.cumsum, np.nancumprod: np.cumprod, np.nanmean: np.mean,
    np.nanmedian: np.median, np.nanpercentile: np.percentile, np.
    nanquantile: np.quantile, np.nanvar: np.var, np.nanstd: np.std}

IDS = [k.__name__ for k in NANFUNCS]

_TEST_ARRAYS = {'0d': np.array(5), '1d': np.array([127, 39, 93, 87, 46])}

_TIME_UNITS = ('Y', 'M', 'W', 'D', 'h', 'm', 's', 'ms', 'us', 'ns', 'ps', 'fs', 'as')

_TYPE_CODES = list(np.typecodes['AllFloat'])

_SWAP_DIRECTION_MAP = {'backward': 'forward', None: 'forward', 'ortho': 'ortho', 'forward':
    'backward'}

EXTRA_LINK_ARGS = []

EXTRA_LIBRARIES = ['npyrandom']

EXTRA_COMPILE_ARGS = ['-U__GNUC_GNU_INLINE__']

LEGACY_DEFS = [('NP_RANDOM_LEGACY', '1')]

PCG64_DEFS = []

JUMP_TEST_DATA = [{'seed': 0, 'steps': 10, 'initial': {'key_sha256':
    'bb1636883c2707b51c5b7fc26c6927af4430f2e0785a8c7bc886337f919f9edf',
    'pos': 9}, 'jumped': {'key_sha256':
    'ff682ac12bb140f2d72fba8d3506cf4e46817a0db27aae1683867629031d8d55',
    'pos': 598}}, {'seed': 384908324, 'steps': 312, 'initial': {
    'key_sha256':
    '16b791a1e04886ccbbb4d448d6ff791267dc458ae599475d08d5cced29d11614',
    'pos': 311}, 'jumped': {'key_sha256':
    'a0110a2cf23b56be0feaed8f787a7fc84bef0cb5623003d75b26bdfa1c18002c',
    'pos': 276}}, {'seed': [839438204, 980239840, 859048019, 821], 'steps':
    511, 'initial': {'key_sha256':
    'd306cf01314d51bd37892d874308200951a35265ede54d200f1e065004c3e9ea',
    'pos': 510}, 'jumped': {'key_sha256':
    '0e00ab449f01a5195a83b4aee0dfbc2ce8d46466a640b92e33977d2e42f777f8',
    'pos': 475}}]

INT_FUNCS = {'binomial': (100.0, 0.6), 'geometric': (0.5,), 'hypergeometric': (20, 20, 
    10), 'logseries': (0.5,), 'multinomial': (20, np.ones(6) / 6.0),
    'negative_binomial': (100, 0.5), 'poisson': (10.0,), 'zipf': (2,)}

INT_FUNC_HASHES = {'binomial':
    '8626dd9d052cb608e93d8868de0a7b347258b199493871a1dc56e2a26cacb112',
    'geometric':
    '8edd53d272e49c4fc8fbbe6c7d08d563d62e482921f3131d0a0e068af30f0db9',
    'hypergeometric':
    '83496cc4281c77b786c9b7ad88b74d42e01603a55c60577ebab81c3ba8d45657',
    'logseries':
    '65878a38747c176bc00e930ebafebb69d4e1e16cd3a704e264ea8f5e24f548db',
    'multinomial':
    '7a984ae6dca26fd25374479e118b22f55db0aedccd5a0f2584ceada33db98605',
    'negative_binomial':
    'd636d968e6a24ae92ab52fe11c46ac45b0897e98714426764e820a7d77602a61',
    'poisson':
    '956552176f77e7c9cb20d0118fc9cf690be488d790ed4b4c4747b965e61b0bb4',
    'zipf': 'f84ba7feffda41e606e20b28dfc0f1ea9964a74574513d4a4cbc98433a8bfa45'}

MISSING_CFFI = (True)

MISSING_CTYPES = (False)

E = ElementMaker(makeelement=html_parser.makeelement)

O = np.ones((10, 10), np.complex128)

T0 = [1]

T3 = [0, -3, 0, 4]

T4 = [1, 0, -8, 0, 8]

T5 = [0, 5, 0, -20, 0, 16]

T6 = [-1, 0, 18, 0, -48, 0, 32]

T7 = [0, -7, 0, 56, 0, -112, 0, 64]

T8 = [1, 0, -32, 0, 160, 0, -256, 0, 128]

T9 = [0, 9, 0, -120, 0, 432, 0, -576, 0, 256]

L0 = np.array([1])

L1 = np.array([0, 1])

L2 = (np.array([-1, 0, 3]) / 2)

L3 = (np.array([0, -3, 0, 5]) / 2)

L4 = (np.array([3, 0, -30, 0, 35]) / 8)

L5 = (np.array([0, 15, 0, -70, 0, 63]) / 8)

L6 = (np.array([-5, 0, 105, 0, -315, 0, 231]) / 16)

L7 = (np.array([0, -35, 0, 315, 0, -693, 0, 429]) / 16)

L8 = (50)

L9 = (np.array([0, 315, 0, -4620, 0, 18018, 0, -25740, 0, 12155]) / 128)

SWITCH_TO_EXP = ('1.0 + (1.0e-01) x + (1.0e-02) x**2', '1.2 + (1.2e-01) x + (1.2e-02) x**2',
    '1.23 + 0.12 x + (1.23e-02) x**2 + (1.23e-03) x**3',
    '1.235 + 0.123 x + (1.235e-02) x**2 + (1.235e-03) x**3',
    '1.2346 + 0.1235 x + 0.0123 x**2 + (1.2346e-03) x**3 + (1.2346e-04) x**4',
    '1.23457 + 0.12346 x + 0.01235 x**2 + (1.23457e-03) x**3 + (1.23457e-04) x**4'
    ,
    '1.234568 + 0.123457 x + 0.012346 x**2 + 0.001235 x**3 + (1.234568e-04) x**4 + (1.234568e-05) x**5'
    ,
    '1.2345679 + 0.1234568 x + 0.0123457 x**2 + 0.0012346 x**3 + (1.2345679e-04) x**4 + (1.2345679e-05) x**5'
    )

H0 = np.array([1])

H1 = E.h1

H2 = E.h2

H3 = E.h3

H4 = E.h4

H5 = E.h5

H6 = E.h6

H7 = np.array([0, -1680, 0, 3360, 0, -1344, 0, 128])

H8 = np.array([1680, 0, -13440, 0, 13440, 0, -3584, 0, 256])

H9 = np.array([0, 30240, 0, -80640, 0, 48384, 0, -9216, 0, 512])

_MAGIC = b'P7 332'

_MODES = {(1, 0): ('1', '1'), (2, 0): ('L', 'L;2'), (4, 0): ('L', 'L;4'), (8, 0): (
    'L', 'L'), (16, 0): ('I;16', 'I;16B'), (8, 2): ('RGB', 'RGB'), (16, 2):
    ('RGB', 'RGB;16B'), (1, 3): ('P', 'P;1'), (2, 3): ('P', 'P;2'), (4, 3):
    ('P', 'P;4'), (8, 3): ('P', 'P'), (8, 4): ('LA', 'LA'), (16, 4): (
    'RGBA', 'LA;16B'), (8, 6): ('RGBA', 'RGBA'), (16, 6): ('RGBA', 'RGBA;16B')}

MAX_TEXT_CHUNK = ImageFile.SAFEBLOCK

MAX_TEXT_MEMORY = (64 * MAX_TEXT_CHUNK)

OP_NONE = (0)

OP_BACKGROUND = (1)

OP_PREVIOUS = (2)

OP_SOURCE = (0)

OP_OVER = (1)

_OUTMODES = {'1': ('1', b'\x01', b'\x00'), 'L;1': ('L;1', b'\x01', b'\x00'), 'L;2': (
    'L;2', b'\x02', b'\x00'), 'L;4': ('L;4', b'\x04', b'\x00'), 'L': ('L',
    b'\x08', b'\x00'), 'LA': ('LA', b'\x08', b'\x04'), 'I': ('I;16B',
    b'\x10', b'\x00'), 'I;16': ('I;16B', b'\x10', b'\x00'), 'I;16B': (
    'I;16B', b'\x10', b'\x00'), 'P;1': ('P;1', b'\x01', b'\x03'), 'P;2': (
    'P;2', b'\x02', b'\x03'), 'P;4': ('P;4', b'\x04', b'\x03'), 'P': ('P',
    b'\x08', b'\x03'), 'RGB': ('RGB', b'\x08', b'\x02'), 'RGBA': ('RGBA',
    b'\x08', b'\x06')}

SAVE = {'1': ('0 1', '1'), 'L': ('Greyscale', 'L'), 'LA': ('LA', 'LA;L'), 'P': (
    'Greyscale', 'P'), 'PA': ('LA', 'PA;L'), 'I': ('L 32S', 'I;32S'),
    'I;16': ('L 16', 'I;16'), 'I;16L': ('L 16L', 'I;16L'), 'I;16B': (
    'L 16B', 'I;16B'), 'F': ('L 32F', 'F;32F'), 'RGB': ('RGB', 'RGB;L'),
    'RGBA': ('RGBA', 'RGBA;L'), 'RGBX': ('RGBX', 'RGBX;L'), 'CMYK': ('CMYK',
    'CMYK;L'), 'YCbCr': ('YCC', 'YCbCr;L')}

MAXBLOCK = (65536)

SAFEBLOCK = (1024 * 1024)

LOAD_TRUNCATED_IMAGES = (False)

ERRORS = {(-1): 'image buffer overrun error', (-2): 'decoding error', (-3):
    'unknown error', (-8): 'bad configuration', (-9): 'out of memory error'}

RGB_AFTER_FIRST = (0)

RGB_AFTER_DIFFERENT_PALETTE_ONLY = (1)

RGB_ALWAYS = (2)

LOADING_STRATEGY = LoadingStrategy.RGB_AFTER_FIRST

RAWMODE = {'1': 'L', 'L': 'L', 'RGB': 'RGB', 'RGBX': 'RGB', 'CMYK': 'CMYK;I', 'YCbCr':
    'YCbCr'}

_FORCE_OPTIMIZE = (False)

_FLAGS = {'MATRIXINPUT': 1, 'MATRIXOUTPUT': 2, 'MATRIXONLY': 1 | 2,
    'NOWHITEONWHITEFIXUP': 4, 'NOPRELINEARIZATION': 16, 'GUESSDEVICECLASS':
    32, 'NOTCACHE': 64, 'NOTPRECALC': 256, 'NULLTRANSFORM': 512,
    'HIGHRESPRECALC': 1024, 'LOWRESPRECALC': 2048, 'WHITEBLACKCOMPENSATION':
    8192, 'BLACKPOINTCOMPENSATION': 8192, 'GAMUTCHECK': 4096,
    'SOFTPROOFING': 16384, 'PRESERVEBLACK': 32768, 'NODEFAULTRESOURCEDEF': 
    16777216, 'GRIDPOINTS': lambda n: (n & 255) << 16}

_COMPRESSION_TYPES = {'none': 255, 'rle': 1, 'scanline': 0}

WIDTH = (4)

IPTCNAA = (33723)

OECF = (34856)

TAGS = {COMMENT: 0, DATE: 0, EQUIPMENT: 0, FRAMES: 0, LUT: 0, NAME: 0, SCALE: 0,
    SIZE: 0, MODE: 0}

GPSDOP = (11)

GPSTAGS = {i.value: i.name for i in GPS}

IFD1 = (-1)

D55 = (20)

D65 = (21)

D75 = (22)

D50 = (23)

ISO = (24)

_DESCRIPTION = """
pyCMS

    a Python / PIL interface to the littleCMS ICC Color Management System
    Copyright (C) 2002-2003 Kevin Cazabon
    kevin@cazabon.com
    https://www.cazabon.com

    pyCMS home page:  https://www.cazabon.com/pyCMS
    littleCMS home page:  https://www.littlecms.com
    (littleCMS is Copyright (C) 1998-2001 Marti Maria)

    Originally released under LGPL.  Graciously donated to PIL in
    March 2009, for distribution under the standard PIL license

    The pyCMS.py module provides a "clean" interface between Python/PIL and
    pyCMSdll, taking care of some of the more complex handling of the direct
    pyCMSdll functions, as well as error-checking and making sure that all
    relevant data is kept together.

    While it is possible to call pyCMSdll functions directly, it's not highly
    recommended.

    Version History:

        1.0.0 pil       Oct 2013 Port to LCMS 2.

        0.1.0 pil mod   March 10, 2009

                        Renamed display profile to proof profile. The proof
                        profile is the profile of the device that is being
                        simulated, not the profile of the device which is
                        actually used to display/print the final simulation
                        (that'd be the output profile) - also see LCMSAPI.txt
                        input colorspace -> using 'renderingIntent' -> proof
                        colorspace -> using 'proofRenderingIntent' -> output
                        colorspace

                        Added LCMS FLAGS support.
                        Added FLAGS["SOFTPROOFING"] as default flag for
                        buildProofTransform (otherwise the proof profile/intent
                        would be ignored).

        0.1.0 pil       March 2009 - added to PIL, as PIL.ImageCms

        0.0.2 alpha     Jan 6, 2002

                        Added try/except statements around type() checks of
                        potential CObjects... Python won't let you use type()
                        on them, and raises a TypeError (stupid, if you ask
                        me!)

                        Added buildProofTransformFromOpenProfiles() function.
                        Additional fixes in DLL, see DLL code for details.

        0.0.1 alpha     first public release, Dec. 26, 2002

    Known to-do list with current version (of Python interface, not pyCMSdll):

        none

"""

_VERSION = """1.0.0 pil"""

PERCEPTUAL = (0)

RELATIVE_COLORIMETRIC = (1)

SATURATION = (2)

ABSOLUTE_COLORIMETRIC = (3)

INPUT = E.input

OUTPUT = (1)

PROOF = (2)

NOCACHE = (64)

NOOPTIMIZE = (256)

NULLTRANSFORM = (512)

GAMUTCHECK = (4096)

SOFTPROOFING = (16384)

BLACKPOINTCOMPENSATION = (8192)

NOWHITEONWHITEFIXUP = (4)

HIGHRESPRECALC = (1024)

LOWRESPRECALC = (2048)

USE_8BITS_DEVICELINK = (8)

GUESSDEVICECLASS = (32)

KEEP_SEQUENCE = (128)

FORCE_CLUT = (2)

CLUT_POST_LINEARIZATION = (1)

CLUT_PRE_LINEARIZATION = (16)

NONEGATIVES = (32768)

COPY_ALPHA = (67108864)

NODEFAULTRESOURCEDEF = (16777216)

_GRIDPOINTS_1 = (1 << 16)

_GRIDPOINTS_2 = (2 << 16)

_GRIDPOINTS_4 = (4 << 16)

_GRIDPOINTS_8 = (8 << 16)

_GRIDPOINTS_16 = (16 << 16)

_GRIDPOINTS_32 = (32 << 16)

_GRIDPOINTS_64 = (64 << 16)

_GRIDPOINTS_128 = (128 << 16)

_MAX_FLAG = reduce(operator.or_, Flags)

MODES = {b'P1': '1', b'P2': 'L', b'P3': 'RGB', b'P4': '1', b'P5': 'L', b'P6': 'RGB',
    b'P0CMYK': 'CMYK', b'Pf': 'F', b'PyP': 'P', b'PyRGBA': 'RGBA',
    b'PyCMYK': 'CMYK'}

EDROFF_PS = b'/S { show } bind def\n/P { moveto show } bind def\n/M { moveto } bind def\n/X { 0 rmoveto } bind def\n/Y { 0 exch rmoveto } bind def\n/E {    findfont\n        dup maxlength dict begin\n        {\n                1 index /FID ne { def } { pop pop } ifelse\n        } forall\n        /Encoding exch def\n        dup /FontName exch def\n        currentdict end definefont pop\n} bind def\n/F {    findfont exch scalefont dup setfont\n        [ exch /setfont cvx ] cvx bind def\n} bind def\n'

VDI_PS = b'/Vm { moveto } bind def\n/Va { newpath arcn stroke } bind def\n/Vl { moveto lineto stroke } bind def\n/Vc { newpath 0 360 arc closepath } bind def\n/Vr {   exch dup 0 rlineto\n        exch dup 0 exch rlineto\n        exch neg 0 rlineto\n        0 exch neg rlineto\n        setgray fill } bind def\n/Tm matrix def\n/Ve {   Tm currentmatrix pop\n        translate scale newpath 0 0 .5 0 360 arc closepath\n        Tm setmatrix\n} bind def\n/Vf { currentgray exch setgray fill setgray } bind def\n'

ERROR_PS = b'/landscape false def\n/errorBUF 200 string def\n/errorNL { currentpoint 10 sub exch pop 72 exch moveto } def\nerrordict begin /handleerror {\n    initmatrix /Courier findfont 10 scalefont setfont\n    newpath 72 720 moveto $error begin /newerror false def\n    (PostScript Error) show errorNL errorNL\n    (Error: ) show\n        /errorname load errorBUF cvs show errorNL errorNL\n    (Command: ) show\n        /command load dup type /stringtype ne { errorBUF cvs } if show\n        errorNL errorNL\n    (VMstatus: ) show\n        vmstatus errorBUF cvs show ( bytes available, ) show\n        errorBUF cvs show ( bytes used at level ) show\n        errorBUF cvs show errorNL errorNL\n    (Operand stargck: ) show errorNL /ostargck load {\n        dup type /stringtype ne { errorBUF cvs } if 72 0 rmoveto show errorNL\n    } forall errorNL\n    (Execution stargck: ) show errorNL /estargck load {\n        dup type /stringtype ne { errorBUF cvs } if 72 0 rmoveto show errorNL\n    } forall\n    end showpage\n} def end\n'

MAGIC = b'FTEX'

EPSILON = _fitz.EPSILON

SEGMENTS = [linear, curved, sine, sphere_increasing, sphere_decreasing]

TKINTER_LIB = None

LUT_SIZE = (1 << 9)

ROTATION_MATRIX = [6, 3, 0, 7, 4, 1, 8, 5, 2]

MIRROR_MATRIX = [2, 1, 0, 5, 4, 3, 8, 7, 6]

PCF_MAGIC = (1885562369)

PCF_PROPERTIES = (1 << 0)

PCF_ACCELERATORS = (1 << 1)

PCF_METRICS = (1 << 2)

PCF_BITMAPS = (1 << 3)

PCF_INK_METRICS = (1 << 4)

PCF_BDF_ENCODINGS = (1 << 5)

PCF_SWIDTHS = (1 << 6)

PCF_GLYPH_NAMES = (1 << 7)

PCF_BDF_ACCELERATORS = (1 << 8)

JPEG = (0)

UNCOMPRESSED = (1)

DXT = (2)

UNCOMPRESSED_RAW_BGRA = (3)

DXT1 = (0)

DXT3 = i32(b'DXT3')

DXT5 = i32(b'DXT5')

SUPPORTED = (False)

_VP8_MODES_BY_IDENTIFIER = {b'VP8 ': 'RGB', b'VP8X': 'RGBA', b'VP8L': 'RGBA'}

BYTE = (1)

ASCII = """ 123456789#"""

SHORT = (3)

LONG = (4)

RATIONAL = (5)

SIGNED_BYTE = (6)

UNDEFINED = (7)

SIGNED_SHORT = (8)

SIGNED_LONG = (9)

SIGNED_RATIONAL = (10)

FLOAT = (2)

DOUBLE = (12)

IFD = (13)

LONG8 = (16)

LIBTIFF_CORE = {255, 256, 257, 258, 259, 262, 263, 266, 274, 277, 278, 280, 281, 340, 341,
    282, 283, 284, 286, 287, 296, 297, 321, 320, 338, 32995, 322, 323, 
    32998, 32996, 339, 32997, 330, 531, 530, 301, 532, 333, 269, 65537}

READ_LIBTIFF = (False)

WRITE_LIBTIFF = (False)

STRIP_SIZE = (65536)

II = b'II'

MM = b'MM'

OSUBFILETYPE = (255)

IMAGEWIDTH = (256)

IMAGELENGTH = (257)

BITSPERSAMPLE = (258)

COMPRESSION = {(1): 'raw', (5): 'jpeg'}

PHOTOMETRIC_INTERPRETATION = (262)

FILLORDER = (266)

IMAGEDESCRIPTION = (270)

STRIPOFFSETS = (273)

SAMPLESPERPIXEL = (277)

ROWSPERSTRIP = (278)

STRIPBYTECOUNTS = (279)

X_RESOLUTION = (282)

Y_RESOLUTION = (283)

PLANAR_CONFIGURATION = (284)

RESOLUTION_UNIT = (296)

TRANSFERFUNCTION = (301)

SOFTWARE = (305)

DATE_TIME = (306)

ARTIST = (315)

PREDICTOR = (317)

COLORMAP = (320)

TILEWIDTH = (322)

TILELENGTH = (323)

TILEOFFSETS = (324)

TILEBYTECOUNTS = (325)

SUBIFD = (330)

EXTRASAMPLES = (338)

SAMPLEFORMAT = (339)

JPEGTABLES = (347)

YCBCRSUBSAMPLING = (530)

REFERENCEBLACKWHITE = (532)

COPYRIGHT = (33432)

IPTC_NAA_CHUNK = (33723)

PHOTOSHOP_CHUNK = (34377)

ICCPROFILE = (34675)

EXIFIFD = (34665)

XMP = (700)

JPEGQUALITY = (65537)

IMAGEJ_META_DATA_BYTE_COUNTS = (50838)

IMAGEJ_META_DATA = (50839)

COMPRESSION_INFO = {(1): 'raw', (2): 'tiff_ccitt', (3): 'group3', (4): 'group4', (5):
    'tiff_lzw', (6): 'tiff_jpeg', (7): 'jpeg', (8): 'tiff_adobe_deflate', (
    32771): 'tiff_raw_16', (32773): 'packbits', (32809): 'tiff_thunderscan',
    (32946): 'tiff_deflate', (34676): 'tiff_sgilog', (34677):
    'tiff_sgilog24', (34925): 'lzma', (50000): 'zstd', (50001): 'webp'}

COMPRESSION_INFO_REV = {v: k for k, v in COMPRESSION_INFO.items()}

OPEN_INFO = {(II, 0, (1,), 1, (1,), ()): ('1', '1;I'), (MM, 0, (1,), 1, (1,), ()): ('1',
    '1;I'), (II, 0, (1,), 2, (1,), ()): ('1', '1;IR'), (MM, 0, (1,), 2, (1,
    ), ()): ('1', '1;IR'), (II, 1, (1,), 1, (1,), ()): ('1', '1'), (MM, 1,
    (1,), 1, (1,), ()): ('1', '1'), (II, 1, (1,), 2, (1,), ()): ('1', '1;R'
    ), (MM, 1, (1,), 2, (1,), ()): ('1', '1;R'), (II, 0, (1,), 1, (2,), ()):
    ('L', 'L;2I'), (MM, 0, (1,), 1, (2,), ()): ('L', 'L;2I'), (II, 0, (1,),
    2, (2,), ()): ('L', 'L;2IR'), (MM, 0, (1,), 2, (2,), ()): ('L', 'L;2IR'
    ), (II, 1, (1,), 1, (2,), ()): ('L', 'L;2'), (MM, 1, (1,), 1, (2,), ()):
    ('L', 'L;2'), (II, 1, (1,), 2, (2,), ()): ('L', 'L;2R'), (MM, 1, (1,), 
    2, (2,), ()): ('L', 'L;2R'), (II, 0, (1,), 1, (4,), ()): ('L', 'L;4I'),
    (MM, 0, (1,), 1, (4,), ()): ('L', 'L;4I'), (II, 0, (1,), 2, (4,), ()):
    ('L', 'L;4IR'), (MM, 0, (1,), 2, (4,), ()): ('L', 'L;4IR'), (II, 1, (1,
    ), 1, (4,), ()): ('L', 'L;4'), (MM, 1, (1,), 1, (4,), ()): ('L', 'L;4'),
    (II, 1, (1,), 2, (4,), ()): ('L', 'L;4R'), (MM, 1, (1,), 2, (4,), ()):
    ('L', 'L;4R'), (II, 0, (1,), 1, (8,), ()): ('L', 'L;I'), (MM, 0, (1,), 
    1, (8,), ()): ('L', 'L;I'), (II, 0, (1,), 2, (8,), ()): ('L', 'L;IR'),
    (MM, 0, (1,), 2, (8,), ()): ('L', 'L;IR'), (II, 1, (1,), 1, (8,), ()):
    ('L', 'L'), (MM, 1, (1,), 1, (8,), ()): ('L', 'L'), (II, 1, (2,), 1, (8
    ,), ()): ('L', 'L'), (MM, 1, (2,), 1, (8,), ()): ('L', 'L'), (II, 1, (1
    ,), 2, (8,), ()): ('L', 'L;R'), (MM, 1, (1,), 2, (8,), ()): ('L', 'L;R'
    ), (II, 1, (1,), 1, (12,), ()): ('I;16', 'I;12'), (II, 0, (1,), 1, (16,
    ), ()): ('I;16', 'I;16'), (II, 1, (1,), 1, (16,), ()): ('I;16', 'I;16'),
    (MM, 1, (1,), 1, (16,), ()): ('I;16B', 'I;16B'), (II, 1, (1,), 2, (16,),
    ()): ('I;16', 'I;16R'), (II, 1, (2,), 1, (16,), ()): ('I', 'I;16S'), (
    MM, 1, (2,), 1, (16,), ()): ('I', 'I;16BS'), (II, 0, (3,), 1, (32,), ()
    ): ('F', 'F;32F'), (MM, 0, (3,), 1, (32,), ()): ('F', 'F;32BF'), (II, 1,
    (1,), 1, (32,), ()): ('I', 'I;32N'), (II, 1, (2,), 1, (32,), ()): ('I',
    'I;32S'), (MM, 1, (2,), 1, (32,), ()): ('I', 'I;32BS'), (II, 1, (3,), 1,
    (32,), ()): ('F', 'F;32F'), (MM, 1, (3,), 1, (32,), ()): ('F', 'F;32BF'
    ), (II, 1, (1,), 1, (8, 8), (2,)): ('LA', 'LA'), (MM, 1, (1,), 1, (8, 8
    ), (2,)): ('LA', 'LA'), (II, 2, (1,), 1, (8, 8, 8), ()): ('RGB', 'RGB'),
    (MM, 2, (1,), 1, (8, 8, 8), ()): ('RGB', 'RGB'), (II, 2, (1,), 2, (8, 8,
    8), ()): ('RGB', 'RGB;R'), (MM, 2, (1,), 2, (8, 8, 8), ()): ('RGB',
    'RGB;R'), (II, 2, (1,), 1, (8, 8, 8, 8), ()): ('RGBA', 'RGBA'), (MM, 2,
    (1,), 1, (8, 8, 8, 8), ()): ('RGBA', 'RGBA'), (II, 2, (1,), 1, (8, 8, 8,
    8), (0,)): ('RGB', 'RGBX'), (MM, 2, (1,), 1, (8, 8, 8, 8), (0,)): (
    'RGB', 'RGBX'), (II, 2, (1,), 1, (8, 8, 8, 8, 8), (0, 0)): ('RGB',
    'RGBXX'), (MM, 2, (1,), 1, (8, 8, 8, 8, 8), (0, 0)): ('RGB', 'RGBXX'),
    (II, 2, (1,), 1, (8, 8, 8, 8, 8, 8), (0, 0, 0)): ('RGB', 'RGBXXX'), (MM,
    2, (1,), 1, (8, 8, 8, 8, 8, 8), (0, 0, 0)): ('RGB', 'RGBXXX'), (II, 2,
    (1,), 1, (8, 8, 8, 8), (1,)): ('RGBA', 'RGBa'), (MM, 2, (1,), 1, (8, 8,
    8, 8), (1,)): ('RGBA', 'RGBa'), (II, 2, (1,), 1, (8, 8, 8, 8, 8), (1, 0
    )): ('RGBA', 'RGBaX'), (MM, 2, (1,), 1, (8, 8, 8, 8, 8), (1, 0)): (
    'RGBA', 'RGBaX'), (II, 2, (1,), 1, (8, 8, 8, 8, 8, 8), (1, 0, 0)): (
    'RGBA', 'RGBaXX'), (MM, 2, (1,), 1, (8, 8, 8, 8, 8, 8), (1, 0, 0)): (
    'RGBA', 'RGBaXX'), (II, 2, (1,), 1, (8, 8, 8, 8), (2,)): ('RGBA',
    'RGBA'), (MM, 2, (1,), 1, (8, 8, 8, 8), (2,)): ('RGBA', 'RGBA'), (II, 2,
    (1,), 1, (8, 8, 8, 8, 8), (2, 0)): ('RGBA', 'RGBAX'), (MM, 2, (1,), 1,
    (8, 8, 8, 8, 8), (2, 0)): ('RGBA', 'RGBAX'), (II, 2, (1,), 1, (8, 8, 8,
    8, 8, 8), (2, 0, 0)): ('RGBA', 'RGBAXX'), (MM, 2, (1,), 1, (8, 8, 8, 8,
    8, 8), (2, 0, 0)): ('RGBA', 'RGBAXX'), (II, 2, (1,), 1, (8, 8, 8, 8), (
    999,)): ('RGBA', 'RGBA'), (MM, 2, (1,), 1, (8, 8, 8, 8), (999,)): (
    'RGBA', 'RGBA'), (II, 2, (1,), 1, (16, 16, 16), ()): ('RGB', 'RGB;16L'),
    (MM, 2, (1,), 1, (16, 16, 16), ()): ('RGB', 'RGB;16B'), (II, 2, (1,), 1,
    (16, 16, 16, 16), ()): ('RGBA', 'RGBA;16L'), (MM, 2, (1,), 1, (16, 16, 
    16, 16), ()): ('RGBA', 'RGBA;16B'), (II, 2, (1,), 1, (16, 16, 16, 16),
    (0,)): ('RGB', 'RGBX;16L'), (MM, 2, (1,), 1, (16, 16, 16, 16), (0,)): (
    'RGB', 'RGBX;16B'), (II, 2, (1,), 1, (16, 16, 16, 16), (1,)): ('RGBA',
    'RGBa;16L'), (MM, 2, (1,), 1, (16, 16, 16, 16), (1,)): ('RGBA',
    'RGBa;16B'), (II, 2, (1,), 1, (16, 16, 16, 16), (2,)): ('RGBA',
    'RGBA;16L'), (MM, 2, (1,), 1, (16, 16, 16, 16), (2,)): ('RGBA',
    'RGBA;16B'), (II, 3, (1,), 1, (1,), ()): ('P', 'P;1'), (MM, 3, (1,), 1,
    (1,), ()): ('P', 'P;1'), (II, 3, (1,), 2, (1,), ()): ('P', 'P;1R'), (MM,
    3, (1,), 2, (1,), ()): ('P', 'P;1R'), (II, 3, (1,), 1, (2,), ()): ('P',
    'P;2'), (MM, 3, (1,), 1, (2,), ()): ('P', 'P;2'), (II, 3, (1,), 2, (2,),
    ()): ('P', 'P;2R'), (MM, 3, (1,), 2, (2,), ()): ('P', 'P;2R'), (II, 3,
    (1,), 1, (4,), ()): ('P', 'P;4'), (MM, 3, (1,), 1, (4,), ()): ('P',
    'P;4'), (II, 3, (1,), 2, (4,), ()): ('P', 'P;4R'), (MM, 3, (1,), 2, (4,
    ), ()): ('P', 'P;4R'), (II, 3, (1,), 1, (8,), ()): ('P', 'P'), (MM, 3,
    (1,), 1, (8,), ()): ('P', 'P'), (II, 3, (1,), 1, (8, 8), (0,)): ('P',
    'PX'), (II, 3, (1,), 1, (8, 8), (2,)): ('PA', 'PA'), (MM, 3, (1,), 1, (
    8, 8), (2,)): ('PA', 'PA'), (II, 3, (1,), 2, (8,), ()): ('P', 'P;R'), (
    MM, 3, (1,), 2, (8,), ()): ('P', 'P;R'), (II, 5, (1,), 1, (8, 8, 8, 8),
    ()): ('CMYK', 'CMYK'), (MM, 5, (1,), 1, (8, 8, 8, 8), ()): ('CMYK',
    'CMYK'), (II, 5, (1,), 1, (8, 8, 8, 8, 8), (0,)): ('CMYK', 'CMYKX'), (
    MM, 5, (1,), 1, (8, 8, 8, 8, 8), (0,)): ('CMYK', 'CMYKX'), (II, 5, (1,),
    1, (8, 8, 8, 8, 8, 8), (0, 0)): ('CMYK', 'CMYKXX'), (MM, 5, (1,), 1, (8,
    8, 8, 8, 8, 8), (0, 0)): ('CMYK', 'CMYKXX'), (II, 5, (1,), 1, (16, 16, 
    16, 16), ()): ('CMYK', 'CMYK;16L'), (MM, 5, (1,), 1, (16, 16, 16, 16),
    ()): ('CMYK', 'CMYK;16B'), (II, 6, (1,), 1, (8,), ()): ('L', 'L'), (MM,
    6, (1,), 1, (8,), ()): ('L', 'L'), (II, 6, (1,), 1, (8, 8, 8), ()): (
    'RGB', 'RGBX'), (MM, 6, (1,), 1, (8, 8, 8), ()): ('RGB', 'RGBX'), (II, 
    8, (1,), 1, (8, 8, 8), ()): ('LAB', 'LAB'), (MM, 8, (1,), 1, (8, 8, 8),
    ()): ('LAB', 'LAB')}

MAX_SAMPLESPERPIXEL = max(len(key_tp[4]) for key_tp in OPEN_INFO)

PREFIXES = [b'MM\x00*', b'II*\x00', b'MM*\x00', b'II\x00*', b'MM\x00+', b'II+\x00']

SAVE_INFO = {'1': ('1', II, 1, 1, (1,), None), 'L': ('L', II, 1, 1, (8,), None), 'LA':
    ('LA', II, 1, 1, (8, 8), 2), 'P': ('P', II, 3, 1, (8,), None), 'PA': (
    'PA', II, 3, 1, (8, 8), 2), 'I': ('I;32S', II, 1, 2, (32,), None),
    'I;16': ('I;16', II, 1, 1, (16,), None), 'I;16S': ('I;16S', II, 1, 2, (
    16,), None), 'F': ('F;32F', II, 1, 3, (32,), None), 'RGB': ('RGB', II, 
    2, 1, (8, 8, 8), None), 'RGBX': ('RGBX', II, 2, 1, (8, 8, 8, 8), 0),
    'RGBA': ('RGBA', II, 2, 1, (8, 8, 8, 8), 2), 'CMYK': ('CMYK', II, 5, 1,
    (8, 8, 8, 8), None), 'YCbCr': ('YCbCr', II, 6, 1, (8, 8, 8), None),
    'LAB': ('LAB', II, 8, 1, (8, 8, 8), None), 'I;32BS': ('I;32BS', MM, 1, 
    2, (32,), None), 'I;16B': ('I;16B', MM, 1, 1, (16,), None), 'I;16BS': (
    'I;16BS', MM, 1, 2, (16,), None), 'F;32BF': ('F;32BF', MM, 1, 3, (32,),
    None)}

BIT2MODE = {(1): ('P', 'P;1'), (4): ('P', 'P;4'), (8): ('P', 'P'), (16): ('RGB',
    'BGR;15'), (24): ('RGB', 'BGR'), (32): ('RGB', 'BGRX')}

COMPRESSIONS = {'RAW': 0, 'RLE8': 1, 'RLE4': 2, 'BITFIELDS': 3, 'JPEG': 4, 'PNG': 5}

MASK_MODES = {(32, (16711680, 65280, 255, 0)): 'BGRX', (32, (4278190080, 16711680, 65280,
    0)): 'XBGR', (32, (4278190080, 65280, 255, 0)): 'BGXR', (32, (
    4278190080, 16711680, 65280, 255)): 'ABGR', (32, (255, 65280, 16711680,
    4278190080)): 'RGBA', (32, (16711680, 65280, 255, 4278190080)): 'BGRA',
    (32, (4278190080, 65280, 255, 16711680)): 'BGAR', (32, (0, 0, 0, 0)):
    'BGRA', (24, (16711680, 65280, 255)): 'BGR', (16, (63488, 2016, 31)):
    'BGR;16', (16, (31744, 992, 31)): 'BGR;15'}

HEADERSIZE = (8)

SIZES = {(512, 512, 2): [(b'ic10', read_png_or_jpeg2000)], (512, 512, 1): [(b'ic09',
    read_png_or_jpeg2000)], (256, 256, 2): [(b'ic14', read_png_or_jpeg2000)
    ], (256, 256, 1): [(b'ic08', read_png_or_jpeg2000)], (128, 128, 2): [(
    b'ic13', read_png_or_jpeg2000)], (128, 128, 1): [(b'ic07',
    read_png_or_jpeg2000), (b'it32', read_32t), (b't8mk', read_mk)], (64, 
    64, 1): [(b'icp6', read_png_or_jpeg2000)], (32, 32, 2): [(b'ic12',
    read_png_or_jpeg2000)], (48, 48, 1): [(b'ih32', read_32), (b'h8mk',
    read_mk)], (32, 32, 1): [(b'icp5', read_png_or_jpeg2000), (b'il32',
    read_32), (b'l8mk', read_mk)], (16, 16, 2): [(b'ic11',
    read_png_or_jpeg2000)], (16, 16, 1): [(b'icp4', read_png_or_jpeg2000),
    (b'is32', read_32), (b's8mk', read_mk)]}

DDS_MAGIC = (542327876)

CAPS = (1)

HEIGHT = (2)

PITCH = (8)

PIXELFORMAT = (4096)

MIPMAPCOUNT = (131072)

LINEARSIZE = (524288)

DEPTH = (8388608)

TEXTURE = (4096)

MIPMAP = (4194304)

CUBEMAP = (512)

CUBEMAP_POSITIVEX = (1024)

CUBEMAP_NEGATIVEX = (2048)

CUBEMAP_POSITIVEY = (4096)

CUBEMAP_NEGATIVEY = (8192)

CUBEMAP_POSITIVEZ = (16384)

CUBEMAP_NEGATIVEZ = (32768)

VOLUME = (2097152)

ALPHAPIXELS = (1)

ALPHA = (2)

FOURCC = (4)

PALETTEINDEXED8 = (32)

RGB = """^[A-Fa-f0-9]{6}$"""

LUMINANCE = (131072)

UNKNOWN = (0)

R32G32B32A32_TYPELESS = (1)

R32G32B32A32_FLOAT = (2)

R32G32B32A32_UINT = (3)

R32G32B32A32_SINT = (4)

R32G32B32_TYPELESS = (5)

R32G32B32_FLOAT = (6)

R32G32B32_UINT = (7)

R32G32B32_SINT = (8)

R16G16B16A16_TYPELESS = (9)

R16G16B16A16_FLOAT = (10)

R16G16B16A16_UNORM = (11)

R16G16B16A16_UINT = (12)

R16G16B16A16_SNORM = (13)

R16G16B16A16_SINT = (14)

R32G32_TYPELESS = (15)

R32G32_FLOAT = (16)

R32G32_UINT = (17)

R32G32_SINT = (18)

R32G8X24_TYPELESS = (19)

D32_FLOAT_S8X24_UINT = (20)

R32_FLOAT_X8X24_TYPELESS = (21)

X32_TYPELESS_G8X24_UINT = (22)

R10G10B10A2_TYPELESS = (23)

R10G10B10A2_UNORM = (24)

R10G10B10A2_UINT = (25)

R11G11B10_FLOAT = (26)

R8G8B8A8_TYPELESS = (27)

R8G8B8A8_UNORM = (28)

R8G8B8A8_UNORM_SRGB = (29)

R8G8B8A8_UINT = (30)

R8G8B8A8_SNORM = (31)

R8G8B8A8_SINT = (32)

R16G16_TYPELESS = (33)

R16G16_FLOAT = (34)

R16G16_UNORM = (35)

R16G16_UINT = (36)

R16G16_SNORM = (37)

R16G16_SINT = (38)

R32_TYPELESS = (39)

D32_FLOAT = (40)

R32_FLOAT = (41)

R32_UINT = (42)

R32_SINT = (43)

R24G8_TYPELESS = (44)

D24_UNORM_S8_UINT = (45)

R24_UNORM_X8_TYPELESS = (46)

X24_TYPELESS_G8_UINT = (47)

R8G8_TYPELESS = (48)

R8G8_UNORM = (49)

R8G8_UINT = (50)

R8G8_SNORM = (51)

R8G8_SINT = (52)

R16_TYPELESS = (53)

R16_FLOAT = (54)

D16_UNORM = (55)

R16_UNORM = (56)

R16_UINT = (57)

R16_SNORM = (58)

R16_SINT = (59)

R8_TYPELESS = (60)

R8_UNORM = (61)

R8_UINT = (62)

R8_SNORM = (63)

R8_SINT = (64)

A8_UNORM = (65)

R1_UNORM = (66)

R9G9B9E5_SHAREDEXP = (67)

R8G8_B8G8_UNORM = (68)

G8R8_G8B8_UNORM = (69)

BC1_TYPELESS = (70)

BC1_UNORM = (71)

BC1_UNORM_SRGB = (72)

BC2_TYPELESS = (73)

BC2_UNORM = (74)

BC2_UNORM_SRGB = (75)

BC3_TYPELESS = (76)

BC3_UNORM = (77)

BC3_UNORM_SRGB = (78)

BC4_TYPELESS = (79)

BC4_UNORM = (80)

BC4_SNORM = (81)

BC5_TYPELESS = (82)

BC5_UNORM = (83)

BC5_SNORM = (84)

B5G6R5_UNORM = (85)

B5G5R5A1_UNORM = (86)

B8G8R8A8_UNORM = (87)

B8G8R8X8_UNORM = (88)

R10G10B10_XR_BIAS_A2_UNORM = (89)

B8G8R8A8_TYPELESS = (90)

B8G8R8A8_UNORM_SRGB = (91)

B8G8R8X8_TYPELESS = (92)

B8G8R8X8_UNORM_SRGB = (93)

BC6H_TYPELESS = (94)

BC6H_UF16 = (95)

BC6H_SF16 = (96)

BC7_TYPELESS = (97)

BC7_UNORM = (98)

BC7_UNORM_SRGB = (99)

AYUV = (100)

Y410 = (101)

Y416 = (102)

NV12 = (103)

P010 = (104)

P016 = (105)

OPAQUE_420 = (106)

YUY2 = i32(b'YUY2')

Y210 = (108)

Y216 = (109)

NV11 = (110)

AI44 = (111)

IA44 = (112)

P8 = (41)

A8P8 = (40)

B4G4R4A4_UNORM = (115)

P208 = (130)

V208 = (131)

V408 = (132)

SAMPLER_FEEDBACK_MIN_MIP_OPAQUE = (189)

SAMPLER_FEEDBACK_MIP_REGION_USED_OPAQUE = (190)

R8G8B8 = (20)

A8R8G8B8 = (21)

X8R8G8B8 = (22)

R5G6B5 = (23)

X1R5G5B5 = (24)

A1R5G5B5 = (25)

A4R4G4B4 = (26)

R3G3B2 = (27)

A8 = (28)

A8R3G3B2 = (29)

X4R4G4B4 = (30)

A2B10G10R10 = (31)

A8B8G8R8 = (32)

X8B8G8R8 = (33)

G16R16 = (34)

A2R10G10B10 = (35)

A16B16G16R16 = (36)

A8L8 = (51)

A4L4 = (52)

V8U8 = (60)

L6V5U5 = (61)

X8L8V8U8 = (62)

Q8W8V8U8 = (63)

V16U16 = (64)

A2W10V10U10 = (67)

D16_LOCKABLE = (70)

D32 = (71)

D15S1 = (73)

D24S8 = (75)

D24X8 = (77)

D24X4S4 = (79)

D16 = (80)

D32F_LOCKABLE = (82)

D24FS8 = (83)

D32_LOCKABLE = (84)

S8_LOCKABLE = (85)

L16 = (81)

VERTEXDATA = (100)

INDEX16 = (101)

INDEX32 = (102)

Q16W16V16U16 = (110)

R16F = (111)

G16R16F = (112)

A16B16G16R16F = (113)

R32F = (114)

G32R32F = (115)

A32B32G32R32F = (116)

A2B10G10R10_XR_BIAS = (119)

BINARYBUFFER = (199)

UYVY = i32(b'UYVY')

R8G8_B8G8 = i32(b'RGBG')

G8R8_G8B8 = i32(b'GRGB')

DXT2 = i32(b'DXT2')

DXT4 = i32(b'DXT4')

DX10 = i32(b'DX10')

BC4S = i32(b'BC4S')

BC4U = i32(b'BC4U')

BC5S = i32(b'BC5S')

BC5U = i32(b'BC5U')

ATI1 = i32(b'ATI1')

ATI2 = i32(b'ATI2')

MULTI2_ARGB8 = i32(b'MET1')

DDS_FOURCC = DDPF.FOURCC

DDS_RGB = DDPF.RGB

DDS_RGBA = (DDPF.RGB | DDPF.ALPHAPIXELS)

DDS_LUMINANCE = DDPF.LUMINANCE

DDS_LUMINANCEA = (DDPF.LUMINANCE | DDPF.ALPHAPIXELS)

DDS_ALPHA = DDPF.ALPHA

DDS_PAL8 = DDPF.PALETTEINDEXED8

DDS_HEADER_FLAGS_TEXTURE = (DDSD.CAPS | DDSD.HEIGHT | DDSD.WIDTH | DDSD.PIXELFORMAT)

DDS_HEADER_FLAGS_MIPMAP = DDSD.MIPMAPCOUNT

DDS_HEADER_FLAGS_VOLUME = DDSD.DEPTH

DDS_HEADER_FLAGS_PITCH = DDSD.PITCH

DDS_HEADER_FLAGS_LINEARSIZE = DDSD.LINEARSIZE

DDS_HEIGHT = DDSD.HEIGHT

DDS_WIDTH = DDSD.WIDTH

DDS_SURFACE_FLAGS_TEXTURE = DDSCAPS.TEXTURE

DDS_SURFACE_FLAGS_MIPMAP = (DDSCAPS.COMPLEX | DDSCAPS.MIPMAP)

DDS_SURFACE_FLAGS_CUBEMAP = DDSCAPS.COMPLEX

DDS_CUBEMAP_POSITIVEX = (DDSCAPS2.CUBEMAP | DDSCAPS2.CUBEMAP_POSITIVEX)

DDS_CUBEMAP_NEGATIVEX = (DDSCAPS2.CUBEMAP | DDSCAPS2.CUBEMAP_NEGATIVEX)

DDS_CUBEMAP_POSITIVEY = (DDSCAPS2.CUBEMAP | DDSCAPS2.CUBEMAP_POSITIVEY)

DDS_CUBEMAP_NEGATIVEY = (DDSCAPS2.CUBEMAP | DDSCAPS2.CUBEMAP_NEGATIVEY)

DDS_CUBEMAP_POSITIVEZ = (DDSCAPS2.CUBEMAP | DDSCAPS2.CUBEMAP_POSITIVEZ)

DDS_CUBEMAP_NEGATIVEZ = (DDSCAPS2.CUBEMAP | DDSCAPS2.CUBEMAP_NEGATIVEZ)

DXT1_FOURCC = D3DFMT.DXT1

DXT3_FOURCC = D3DFMT.DXT3

DXT5_FOURCC = D3DFMT.DXT5

DXGI_FORMAT_R8G8B8A8_TYPELESS = DXGI_FORMAT.R8G8B8A8_TYPELESS

DXGI_FORMAT_R8G8B8A8_UNORM = DXGI_FORMAT.R8G8B8A8_UNORM

DXGI_FORMAT_R8G8B8A8_UNORM_SRGB = DXGI_FORMAT.R8G8B8A8_UNORM_SRGB

DXGI_FORMAT_BC5_TYPELESS = DXGI_FORMAT.BC5_TYPELESS

DXGI_FORMAT_BC5_UNORM = DXGI_FORMAT.BC5_UNORM

DXGI_FORMAT_BC5_SNORM = DXGI_FORMAT.BC5_SNORM

DXGI_FORMAT_BC6H_UF16 = DXGI_FORMAT.BC6H_UF16

DXGI_FORMAT_BC6H_SF16 = DXGI_FORMAT.BC6H_SF16

DXGI_FORMAT_BC7_TYPELESS = DXGI_FORMAT.BC7_TYPELESS

DXGI_FORMAT_BC7_UNORM = DXGI_FORMAT.BC7_UNORM

DXGI_FORMAT_BC7_UNORM_SRGB = DXGI_FORMAT.BC7_UNORM_SRGB

FLIP_LEFT_RIGHT = (0)

FLIP_TOP_BOTTOM = (1)

ROTATE_90 = (2)

ROTATE_180 = (3)

ROTATE_270 = (4)

TRANSPOSE = (5)

TRANSVERSE = (6)

AFFINE = (0)

EXTENT = (1)

PERSPECTIVE = (2)

QUAD = (3)

MESH = (4)

NEAREST = (0)

BOX = (4)

BILINEAR = (2)

HAMMING = (5)

BICUBIC = (3)

LANCZOS = (1)

ORDERED = (1)

RASTERIZE = (2)

FLOYDSTEINBERG = (3)

WEB = (0)

ADAPTIVE = (1)

MEDIANCUT = (0)

MAXCOVERAGE = (1)

FASTOCTREE = (2)

LIBIMAGEQUANT = (3)

DEFAULT_STRATEGY = core.DEFAULT_STRATEGY

FILTERED = core.FILTERED

HUFFMAN_ONLY = core.HUFFMAN_ONLY

RLE = core.RLE

FIXED = core.FIXED

_ENDIAN = ('<' if sys.byteorder == 'little' else '>')

_MAPMODES = ('L', 'P', 'RGBX', 'RGBA', 'CMYK', 'I;16', 'I;16L', 'I;16B')

PALETTE = (PALETTE + (o8(r * 255 // 7) + o8(g * 255 // 7) + o8(b * 255 // 3)))

COMMENT = """Comment"""

DATE = (True)

EQUIPMENT = """Digitalization equipment"""

FRAMES = """File size (no of images)"""

LUT = """Lut"""

NAME = """importlib"""

SCALE = """Scale (x,y)"""

SIZE = """Image size (x*y)"""

MODE = """Image type"""

OPEN = """OPEN"""

MARKER = {(65472): ('SOF0', 'Baseline DCT', SOF), (65473): ('SOF1',
    'Extended Sequential DCT', SOF), (65474): ('SOF2', 'Progressive DCT',
    SOF), (65475): ('SOF3', 'Spatial lossless', SOF), (65476): ('DHT',
    'Define Huffman table', Skip), (65477): ('SOF5',
    'Differential sequential DCT', SOF), (65478): ('SOF6',
    'Differential progressive DCT', SOF), (65479): ('SOF7',
    'Differential spatial', SOF), (65480): ('JPG', 'Extension', None), (
    65481): ('SOF9', 'Extended sequential DCT (AC)', SOF), (65482): (
    'SOF10', 'Progressive DCT (AC)', SOF), (65483): ('SOF11',
    'Spatial lossless DCT (AC)', SOF), (65484): ('DAC',
    'Define arithmetic coding conditioning', Skip), (65485): ('SOF13',
    'Differential sequential DCT (AC)', SOF), (65486): ('SOF14',
    'Differential progressive DCT (AC)', SOF), (65487): ('SOF15',
    'Differential spatial (AC)', SOF), (65488): ('RST0', 'Restart 0', None),
    (65489): ('RST1', 'Restart 1', None), (65490): ('RST2', 'Restart 2',
    None), (65491): ('RST3', 'Restart 3', None), (65492): ('RST4',
    'Restart 4', None), (65493): ('RST5', 'Restart 5', None), (65494): (
    'RST6', 'Restart 6', None), (65495): ('RST7', 'Restart 7', None), (
    65496): ('SOI', 'Start of image', None), (65497): ('EOI',
    'End of image', None), (65498): ('SOS', 'Start of scan', Skip), (65499):
    ('DQT', 'Define quantization table', DQT), (65500): ('DNL',
    'Define number of lines', Skip), (65501): ('DRI',
    'Define restart interval', Skip), (65502): ('DHP',
    'Define hierarchical progression', SOF), (65503): ('EXP',
    'Expand reference component', Skip), (65504): ('APP0',
    'Application segment 0', APP), (65505): ('APP1',
    'Application segment 1', APP), (65506): ('APP2',
    'Application segment 2', APP), (65507): ('APP3',
    'Application segment 3', APP), (65508): ('APP4',
    'Application segment 4', APP), (65509): ('APP5',
    'Application segment 5', APP), (65510): ('APP6',
    'Application segment 6', APP), (65511): ('APP7',
    'Application segment 7', APP), (65512): ('APP8',
    'Application segment 8', APP), (65513): ('APP9',
    'Application segment 9', APP), (65514): ('APP10',
    'Application segment 10', APP), (65515): ('APP11',
    'Application segment 11', APP), (65516): ('APP12',
    'Application segment 12', APP), (65517): ('APP13',
    'Application segment 13', APP), (65518): ('APP14',
    'Application segment 14', APP), (65519): ('APP15',
    'Application segment 15', APP), (65520): ('JPG0', 'Extension 0', None),
    (65521): ('JPG1', 'Extension 1', None), (65522): ('JPG2', 'Extension 2',
    None), (65523): ('JPG3', 'Extension 3', None), (65524): ('JPG4',
    'Extension 4', None), (65525): ('JPG5', 'Extension 5', None), (65526):
    ('JPG6', 'Extension 6', None), (65527): ('JPG7', 'Extension 7', None),
    (65528): ('JPG8', 'Extension 8', None), (65529): ('JPG9', 'Extension 9',
    None), (65530): ('JPG10', 'Extension 10', None), (65531): ('JPG11',
    'Extension 11', None), (65532): ('JPG12', 'Extension 12', None), (65533
    ): ('JPG13', 'Extension 13', None), (65534): ('COM', 'Comment', COM)}

MAX_BYTES_IN_MARKER = (65533)

BASIC = (0)

RAQM = (1)

MAX_STRING_LENGTH = (1000000)

PYTHON_REQUIRES = (3, 8)

PIP_SOURCES_ROOT = dirname(dirname(__file__))

CONFIG_BASENAME = ('pip.ini' if WINDOWS else 'pip.conf')

ENV_NAMES_IGNORED = ('version', 'help')

OVERRIDE_ORDER = (kinds.GLOBAL, kinds.USER, kinds.SITE, kinds.ENV, kinds.ENV_VAR)

VALID_LOAD_ONLY = (kinds.USER, kinds.GLOBAL, kinds.SITE)

ORIGIN_JSON_NAME = """origin.json"""

_DEFAULT_EXTERNALLY_MANAGED_ERROR = f"""The Python environment under {sys.prefix} is managed externally, and may not be
manipulated by the user. Please use specific tooling from the distributor of
the Python installation to interact with this environment instead.
"""

_WEEK = datetime.timedelta(days=7)

KEYRING_DISABLED = (True)

CI_ENVIRONMENT_VARIABLES = ('BUILD_BUILDID', 'BUILD_ID', 'CI', 'PIP_IS_CI')

DOWNLOAD_CHUNK_SIZE = (256 * 1024)

FILE_CHUNK_SIZE = (1024 * 1024)

WINDOWS = (platform.system() == 'Windows')

ENCODING_RE = re.compile(b'coding[:=]\\s*([-\\w.]+)')

DEPRECATION_MSG_PREFIX = """DEPRECATION: """

LEADING_CHARS = """-~.=%0123456789"""

_SETUPTOOLS_SHIM = textwrap.dedent(
    """
    exec(compile('''
    # This is <pip-setuptools-caller> -- a caller that pip uses to run setup.py
    #
    # - It imports setuptools before invoking setup.py, to enable projects that directly
    #   import from `distutils.core` to work with newer packaging standards.
    # - It provides a clear error message when setuptools is not installed.
    # - It sets `sys.argv[0]` to the underlying `setup.py`, when invoking `setup.py` so
    #   setuptools doesn't think the script is `-c`. This avoids the following warning:
    #     manifest_maker: standard file '-c' not found".
    # - It generates a shim setup.py, for handling setup.cfg-only projects.
    import os, sys, tokenize

    try:
        import setuptools
    except ImportError as error:
        print(
            "ERROR: Can not execute `setup.py` since setuptools is not available in "
            "the build environment.",
            file=sys.stderr,
        )
        sys.exit(1)

    __file__ = %r
    sys.argv[0] = __file__

    if os.path.exists(__file__):
        filename = __file__
        with tokenize.open(__file__) as f:
            setup_py_code = f.read()
    else:
        filename = "<auto-generated setuptools caller>"
        setup_py_code = "from setuptools import setup; setup()"

    exec(compile(setup_py_code, filename, "exec"))
    ''' % ({!r},), "<pip-setuptools-caller>", "exec"))
    """
    ).rstrip()

_EXECUTABLE_NAMES = [''.join(parts) for parts in itertools.product(_EXECUTABLE_NAMES,
    _allowed_extensions)]

WHEEL_EXTENSION = """.whl"""

ARCHIVE_EXTENSIONS = ('.tar.gz', '.tar.bz2', '.tar', '.zip', '.tgz', '.tbz', '.whl')

FAVORITE_HASH = """sha256"""

STRONG_HASHES = ['sha256', 'sha384', 'sha512']

_INCLUDE_SYSTEM_SITE_PACKAGES_REGEX = re.compile('include-system-site-packages\\s*=\\s*(?P<value>true|false)')

VERBOSE = (15)

VERSION_COMPATIBLE = (1, 0)

SUPPORTED_EXTENSIONS = (ZIP_EXTENSIONS + TAR_EXTENSIONS)

_SUPPORTED_HASHES = ('sha512', 'sha384', 'sha256', 'sha224', 'sha1', 'md5')

DIRECT_URL_METADATA_NAME = """direct_url.json"""

ENV_VAR_RE = re.compile('(?P<var>\\$\\{(?P<name>[A-Z0-9_]+)\\})')

SCHEME_KEYS = ('purelib', 'platlib', 'headers', 'scripts', 'data')

TYPE_CHECKER = Option.TYPE_CHECKER.copy()

ALWAYS_ENABLED_FEATURES = ['truststore', 'no-binary-enable-wheel-cache']

SUCCESS = (0)

ERROR = """ERROR"""

UNKNOWN_ERROR = (2)

VIRTUALENV_NOT_FOUND = (3)

PREVIOUS_BUILD_DIR_ERROR = (4)

NO_MATCHES_FOUND = (23)

HIDE_CURSOR = (6)

SHOW_CURSOR = (5)

KEEPABLE_TEMPDIR_TYPES = [tempdir_kinds.BUILD_ENV, tempdir_kinds.EPHEM_WHEEL_CACHE, tempdir_kinds.
    REQ_BUILD]

SCHEME_RE = re.compile('^(?:[a-zA-Z][a-zA-Z0-9+-]*:|/)')

COMMENT_RE = re.compile('(^|\\s+)#.*$')

SUPPORTED_OPTIONS_REQ_DEST = [str(o().dest) for o in SUPPORTED_OPTIONS_REQ]

SUPPORTED_OPTIONS_EDITABLE_REQ_DEST = [str(o().dest) for o in SUPPORTED_OPTIONS_EDITABLE_REQ]

REQUIRES_PYTHON_IDENTIFIER = cast(NormalizedName, '<Python from Requires-Python>')

GIT_VERSION_REGEX = re.compile('^git version (\\d+)\\.(\\d+)(?:\\.(\\d+))?.*$')

HASH_REGEX = re.compile('^[a-fA-F0-9]{40}$')

SCP_REGEX = re.compile(
    """^
    # Optional user, e.g. 'git@'
    (\\w+@)?
    # Server, e.g. 'github.com'.
    ([^/:]+):
    # The server-side path. e.g. 'user/project.git'. Must start with an
    # alphanumeric character so as not to be confusable with a Windows paths
    # like 'C:/foo/bar' or 'C:\\foo\\bar'.
    (\\w[^:]*)
    $"""
    , re.VERBOSE)

_USE_SYSCONFIG_DEFAULT = (sys.version_info >= (3, 10))

_USE_SYSCONFIG = _should_use_sysconfig()

_MISMATCH_LEVEL = logging.DEBUG

_AVAILABLE_SCHEMES = set(sysconfig.get_scheme_names())

_PREFERRED_SCHEME_API = getattr(sysconfig, 'get_preferred_scheme', None)

_HOME_KEYS = ['installed_base', 'base', 'installed_platbase', 'platbase', 'prefix',
    'exec_prefix']

USER_CACHE_DIR = appdirs.user_cache_dir('pip')

BASE_COMPLETION = """
# pip {shell} completion start{script}# pip {shell} completion end
"""

COMPLETION_SCRIPTS = {'bash':
    """
        _pip_completion()
        {{
            COMPREPLY=( $( COMP_WORDS="${{COMP_WORDS[*]}}" \\
                           COMP_CWORD=$COMP_CWORD \\
                           PIP_AUTO_COMPLETE=1 $1 2>/dev/null ) )
        }}
        complete -o default -F _pip_completion {prog}
    """
    , 'zsh':
    """
        #compdef -P pip[0-9.]#
        __pip() {{
          compadd $( COMP_WORDS="$words[*]" \\
                     COMP_CWORD=$((CURRENT-1)) \\
                     PIP_AUTO_COMPLETE=1 $words[1] 2>/dev/null )
        }}
        if [[ $zsh_eval_context[-1] == loadautofunc ]]; then
          # autoload from fpath, call function directly
          __pip "$@"
        else
          # eval/source/. command, register function for later
          compdef __pip -P 'pip[0-9.]#'
        fi
    """
    , 'fish':
    """
        function __fish_complete_pip
            set -lx COMP_WORDS (commandline -o) ""
            set -lx COMP_CWORD ( \\
                math (contains -i -- (commandline -t) $COMP_WORDS)-1 \\
            )
            set -lx PIP_AUTO_COMPLETE 1
            string split \\  -- (eval $COMP_WORDS[1])
        end
        complete -fa "(__fish_complete_pip)" -c {prog}
    """
    , 'powershell':
    """
        if ((Test-Path Function:\\TabExpansion) -and -not `
            (Test-Path Function:\\_pip_completeBackup)) {{
            Rename-Item Function:\\TabExpansion _pip_completeBackup
        }}
        function TabExpansion($line, $lastWord) {{
            $lastBlock = [regex]::Split($line, '[|;]')[-1].TrimStart()
            if ($lastBlock.StartsWith("{prog} ")) {{
                $Env:COMP_WORDS=$lastBlock
                $Env:COMP_CWORD=$lastBlock.Split().Length - 1
                $Env:PIP_AUTO_COMPLETE=1
                (& {prog}).Split()
                Remove-Item Env:COMP_WORDS
                Remove-Item Env:COMP_CWORD
                Remove-Item Env:PIP_AUTO_COMPLETE
            }}
            elseif (Test-Path Function:\\_pip_completeBackup) {{
                # Fall back on existing tab expansion
                _pip_completeBackup $line $lastWord
            }}
        }}
    """
    }

METADATA_FIELDS = [('Metadata-Version', False), ('Name', False), ('Version', False), (
    'Dynamic', True), ('Platform', True), ('Supported-Platform', True), (
    'Summary', False), ('Description', False), ('Description-Content-Type',
    False), ('Keywords', False), ('Home-page', False), ('Download-URL', 
    False), ('Author', False), ('Author-email', False), ('Maintainer', 
    False), ('Maintainer-email', False), ('License', False), ('Classifier',
    True), ('Requires-Dist', True), ('Requires-Python', False), (
    'Requires-External', True), ('Project-URL', True), ('Provides-Extra', 
    True), ('Provides-Dist', True), ('Obsoletes-Dist', True)]

DEBUNDLED = (False)

WHEEL_DIR = os.path.abspath(os.path.dirname(__file__))

PEP_560 = (True)

_PEP_696_IMPLEMENTED = (sys.version_info >= (3, 13, 0, 'beta'))

KT = typing.TypeVar('KT')

VT = typing.TypeVar('VT')

TYPE_CHECKING = (False)

_PROTO_ALLOWLIST = {'collections.abc': ['Callable', 'Awaitable', 'Iterable', 'Iterator',
    'AsyncIterable', 'Hashable', 'Sized', 'Container', 'Collection',
    'Reversible', 'Buffer'], 'contextlib': ['AbstractContextManager',
    'AbstractAsyncContextManager'], 'typing_extensions': ['Buffer']}

_EXCLUDED_ATTRS = (frozenset(typing.EXCLUDED_ATTRIBUTES) | {'__match_args__',
    '__protocol_attrs__', '__non_callable_proto_members__', '__final__'})

_PEP_728_IMPLEMENTED = (False)

_TAKES_MODULE = ('module' in inspect.signature(typing._type_check).parameters)

_TYPEDDICT_TYPES = (_TypedDictMeta,)

_UNPACK_DOC = """Type unpack operator.

The type unpack operator takes the child types from some container type,
such as `tuple[int, str]` or a `TypeVarTuple`, and 'pulls them out'. For
example:

  # For some generic class `Foo`:
  Foo[Unpack[tuple[int, str]]]  # Equivalent to Foo[int, str]

  Ts = TypeVarTuple('Ts')
  # Specifies that `Bar` is generic in an arbitrary number of types.
  # (Think of `Ts` as a tuple of an arbitrary number of individual
  #  `TypeVar`s, which the `Unpack` is 'pulling out' directly into the
  #  `Generic[]`.)
  class Bar(Generic[Unpack[Ts]]): ...
  Bar[int]  # Valid
  Bar[int, str]  # Also valid

From Python 3.11, this can also be done using the `*` operator:

    Foo[*tuple[int, str]]
    class Bar(Generic[*Ts]): ...

The operator can also be used along with a `TypedDict` to annotate
`**kwargs` in a function signature. For instance:

  class Movie(TypedDict):
    name: str
    year: int

  # This function expects two keyword arguments - *name* of type `str` and
  # *year* of type `int`.
  def foo(**kwargs: Unpack[Movie]): ...

Note that there is only some runtime checking of this operator. Not
everything the runtime allows may be accepted by static type checkers.

For more information, see PEP 646 and PEP 692.
"""

_ASSERT_NEVER_REPR_MAX_LENGTH = (100)

_F = TypeVar('_F')

_TYPEVARTUPLE_TYPES = {TypeVarTuple, getattr(typing, 'TypeVarTuple', None)}

_CAPI = getattr(_socket, 'CAPI', None)

IO = typing.IO

_CA_FILE_CANDIDATES = ['/etc/ssl/cert.pem', '/etc/pki/tls/cert.pem',
    '/etc/ssl/certs/ca-certificates.crt', '/etc/ssl/ca-bundle.pem']

_HASHED_CERT_FILENAME_RE = re.compile('^[0-9a-fA-F]{8}\\.[0-9]$')

HCERTCHAINENGINE = HANDLE

HCERTSTORE = HANDLE

HCRYPTPROV_LEGACY = HANDLE

PCERT_CONTEXT = POINTER(CERT_CONTEXT)

PCCERT_CONTEXT = POINTER(PCERT_CONTEXT)

PCERT_ENHKEY_USAGE = POINTER(CERT_ENHKEY_USAGE)

PCERT_CHAIN_PARA = POINTER(CERT_CHAIN_PARA)

PCERT_CHAIN_ELEMENT = POINTER(CERT_CHAIN_ELEMENT)

PCERT_SIMPLE_CHAIN = POINTER(CERT_SIMPLE_CHAIN)

PCERT_CHAIN_CONTEXT = POINTER(CERT_CHAIN_CONTEXT)

PCCERT_CHAIN_CONTEXT = POINTER(PCERT_CHAIN_CONTEXT)

PCERT_CHAIN_POLICY_PARA = POINTER(CERT_CHAIN_POLICY_PARA)

PCERT_CHAIN_POLICY_STATUS = POINTER(CERT_CHAIN_POLICY_STATUS)

PCERT_CHAIN_ENGINE_CONFIG = POINTER(CERT_CHAIN_ENGINE_CONFIG)

PHCERTCHAINENGINE = POINTER(HCERTCHAINENGINE)

X509_ASN_ENCODING = (1)

PKCS_7_ASN_ENCODING = (65536)

CERT_STORE_PROV_MEMORY = b'Memory'

CERT_STORE_ADD_USE_EXISTING = (2)

USAGE_MATCH_TYPE_OR = (1)

OID_PKIX_KP_SERVER_AUTH = c_char_p(b'1.3.6.1.5.5.7.3.1')

CERT_CHAIN_REVOCATION_CHECK_END_CERT = (268435456)

CERT_CHAIN_REVOCATION_CHECK_CHAIN = (536870912)

CERT_CHAIN_POLICY_IGNORE_ALL_NOT_TIME_VALID_FLAGS = (7)

CERT_CHAIN_POLICY_IGNORE_INVALID_BASIC_CONSTRAINTS_FLAG = (8)

CERT_CHAIN_POLICY_ALLOW_UNKNOWN_CA_FLAG = (16)

CERT_CHAIN_POLICY_IGNORE_INVALID_NAME_FLAG = (64)

CERT_CHAIN_POLICY_IGNORE_WRONG_USAGE_FLAG = (32)

CERT_CHAIN_POLICY_IGNORE_INVALID_POLICY_FLAG = (128)

CERT_CHAIN_POLICY_IGNORE_ALL_REV_UNKNOWN_FLAGS = (3840)

CERT_CHAIN_POLICY_ALLOW_TESTROOT_FLAG = (32768)

CERT_CHAIN_POLICY_TRUST_TESTROOT_FLAG = (16384)

SECURITY_FLAG_IGNORE_CERT_CN_INVALID = (4096)

AUTHTYPE_SERVER = (2)

CERT_CHAIN_POLICY_SSL = (4)

FORMAT_MESSAGE_FROM_SYSTEM = (4096)

FORMAT_MESSAGE_IGNORE_INSERTS = (512)

CERT_CHAIN_POLICY_VERIFY_MODE_NONE_FLAGS = (CERT_CHAIN_POLICY_IGNORE_ALL_NOT_TIME_VALID_FLAGS |
    CERT_CHAIN_POLICY_IGNORE_INVALID_BASIC_CONSTRAINTS_FLAG |
    CERT_CHAIN_POLICY_ALLOW_UNKNOWN_CA_FLAG |
    CERT_CHAIN_POLICY_IGNORE_INVALID_NAME_FLAG |
    CERT_CHAIN_POLICY_IGNORE_WRONG_USAGE_FLAG |
    CERT_CHAIN_POLICY_IGNORE_INVALID_POLICY_FLAG |
    CERT_CHAIN_POLICY_IGNORE_ALL_REV_UNKNOWN_FLAGS |
    CERT_CHAIN_POLICY_ALLOW_TESTROOT_FLAG |
    CERT_CHAIN_POLICY_TRUST_TESTROOT_FLAG)

USING_STRINGBUILDER = (False)

EX_SKIP = (0)

EX_CONSTRUCT = (1)

EX_READ_ARRAY_HEADER = (2)

EX_READ_MAP_HEADER = (3)

TYPE_IMMEDIATE = (0)

TYPE_ARRAY = (1)

TYPE_MAP = (2)

TYPE_RAW = (3)

TYPE_BIN = (4)

TYPE_EXT = (5)

DEFAULT_RECURSE_LIMIT = (511)

_NO_FORMAT_USED = """"""

_MSGPACK_HEADERS = {(196): (1, _NO_FORMAT_USED, TYPE_BIN), (197): (2, '>H', TYPE_BIN), (198):
    (4, '>I', TYPE_BIN), (199): (2, 'Bb', TYPE_EXT), (200): (3, '>Hb',
    TYPE_EXT), (201): (5, '>Ib', TYPE_EXT), (202): (4, '>f'), (203): (8,
    '>d'), (204): (1, _NO_FORMAT_USED), (205): (2, '>H'), (206): (4, '>I'),
    (207): (8, '>Q'), (208): (1, 'b'), (209): (2, '>h'), (210): (4, '>i'),
    (211): (8, '>q'), (212): (1, 'b1s', TYPE_EXT), (213): (2, 'b2s',
    TYPE_EXT), (214): (4, 'b4s', TYPE_EXT), (215): (8, 'b8s', TYPE_EXT), (
    216): (16, 'b16s', TYPE_EXT), (217): (1, _NO_FORMAT_USED, TYPE_RAW), (
    218): (2, '>H', TYPE_RAW), (219): (4, '>I', TYPE_RAW), (220): (2, '>H',
    TYPE_ARRAY), (221): (4, '>I', TYPE_ARRAY), (222): (2, '>H', TYPE_MAP),
    (223): (4, '>I', TYPE_MAP)}

STANDARD_TYPES = {Token: '', Text: '', Whitespace: 'w', Escape: 'esc', Error: 'err', Other:
    'x', Keyword: 'k', Keyword.Constant: 'kc', Keyword.Declaration: 'kd',
    Keyword.Namespace: 'kn', Keyword.Pseudo: 'kp', Keyword.Reserved: 'kr',
    Keyword.Type: 'kt', Name: 'n', Name.Attribute: 'na', Name.Builtin: 'nb',
    Name.Builtin.Pseudo: 'bp', Name.Class: 'nc', Name.Constant: 'no', Name.
    Decorator: 'nd', Name.Entity: 'ni', Name.Exception: 'ne', Name.Function:
    'nf', Name.Function.Magic: 'fm', Name.Property: 'py', Name.Label: 'nl',
    Name.Namespace: 'nn', Name.Other: 'nx', Name.Tag: 'nt', Name.Variable:
    'nv', Name.Variable.Class: 'vc', Name.Variable.Global: 'vg', Name.
    Variable.Instance: 'vi', Name.Variable.Magic: 'vm', Literal: 'l',
    Literal.Date: 'ld', String: 's', String.Affix: 'sa', String.Backtick:
    'sb', String.Char: 'sc', String.Delimiter: 'dl', String.Doc: 'sd',
    String.Double: 's2', String.Escape: 'se', String.Heredoc: 'sh', String.
    Interpol: 'si', String.Other: 'sx', String.Regex: 'sr', String.Single:
    's1', String.Symbol: 'ss', Number: 'm', Number.Bin: 'mb', Number.Float:
    'mf', Number.Hex: 'mh', Number.Integer: 'mi', Number.Integer.Long: 'il',
    Number.Oct: 'mo', Operator: 'o', Operator.Word: 'ow', Punctuation: 'p',
    Punctuation.Marker: 'pm', Comment: 'c', Comment.Hashbang: 'ch', Comment
    .Multiline: 'cm', Comment.Preproc: 'cp', Comment.PreprocFile: 'cpf',
    Comment.Single: 'c1', Comment.Special: 'cs', Generic: 'g', Generic.
    Deleted: 'gd', Generic.Emph: 'ge', Generic.Error: 'gr', Generic.Heading:
    'gh', Generic.Inserted: 'gi', Generic.Output: 'go', Generic.Prompt:
    'gp', Generic.Strong: 'gs', Generic.Subheading: 'gu', Generic.
    EmphStrong: 'ges', Generic.Traceback: 'gt'}

MODULEDOC = """
.. module:: %s

%s
%s
"""

LEXERDOC = """
.. class:: %s

    :Short names: %s
    :Filenames:   %s
    :MIME types:  %s

    %s

    %s

"""

FMTERDOC = """
.. class:: %s

    :Short names: %s
    :Filenames: %s

    %s

"""

FILTERDOC = """
.. class:: %s

    :Name: %s

    %s

"""

CS_ESCAPE = re.compile('[\\[\\^\\\\\\-\\]]')

FIRST_ELEMENT = itemgetter(0)

LEXER_ENTRY_POINT = """pygments.lexers"""

FORMATTER_ENTRY_POINT = """pygments.formatters"""

STYLE_ENTRY_POINT = """pygments.styles"""

FILTER_ENTRY_POINT = """pygments.filters"""

FILTERS = {'codetagify': CodeTagFilter, 'keywordcase': KeywordCaseFilter, 'highlight':
    NameHighlightFilter, 'raiseonerror': RaiseOnErrorTokenFilter,
    'whitespace': VisibleWhitespaceFilter, 'gobble': GobbleFilter,
    'tokenmerge': TokenMergeFilter, 'symbols': SymbolFilter}

COMPAT = """compat"""

EXTRA_KEYWORDS = {'abs', 'absolute', 'accumulate', 'add', 'alen', 'all', 'allclose',
    'alltrue', 'alterdot', 'amax', 'amin', 'angle', 'any', 'append',
    'apply_along_axis', 'apply_over_axes', 'arange', 'arccos', 'arccosh',
    'arcsin', 'arcsinh', 'arctan', 'arctan2', 'arctanh', 'argmax', 'argmin',
    'argsort', 'argwhere', 'around', 'array', 'array2string', 'array_equal',
    'array_equiv', 'array_repr', 'array_split', 'array_str', 'arrayrange',
    'asanyarray', 'asarray', 'asarray_chkfinite', 'ascontiguousarray',
    'asfarray', 'asfortranarray', 'asmatrix', 'asscalar', 'astype',
    'atleast_1d', 'atleast_2d', 'atleast_3d', 'average', 'bartlett',
    'base_repr', 'beta', 'binary_repr', 'bincount', 'binomial',
    'bitwise_and', 'bitwise_not', 'bitwise_or', 'bitwise_xor', 'blackman',
    'bmat', 'broadcast', 'byte_bounds', 'bytes', 'byteswap', 'c_',
    'can_cast', 'ceil', 'choose', 'clip', 'column_stack', 'common_type',
    'compare_chararrays', 'compress', 'concatenate', 'conj', 'conjugate',
    'convolve', 'copy', 'corrcoef', 'correlate', 'cos', 'cosh', 'cov',
    'cross', 'cumprod', 'cumproduct', 'cumsum', 'delete', 'deprecate',
    'diag', 'diagflat', 'diagonal', 'diff', 'digitize', 'disp', 'divide',
    'dot', 'dsplit', 'dstack', 'dtype', 'dump', 'dumps', 'ediff1d', 'empty',
    'empty_like', 'equal', 'exp', 'expand_dims', 'expm1', 'extract', 'eye',
    'fabs', 'fastCopyAndTranspose', 'fft', 'fftfreq', 'fftshift', 'fill',
    'finfo', 'fix', 'flat', 'flatnonzero', 'flatten', 'fliplr', 'flipud',
    'floor', 'floor_divide', 'fmod', 'frexp', 'fromarrays', 'frombuffer',
    'fromfile', 'fromfunction', 'fromiter', 'frompyfunc', 'fromstring',
    'generic', 'get_array_wrap', 'get_include', 'get_numarray_include',
    'get_numpy_include', 'get_printoptions', 'getbuffer', 'getbufsize',
    'geterr', 'geterrcall', 'geterrobj', 'getfield', 'gradient', 'greater',
    'greater_equal', 'gumbel', 'hamming', 'hanning', 'histogram',
    'histogram2d', 'histogramdd', 'hsplit', 'hstack', 'hypot', 'i0',
    'identity', 'ifft', 'imag', 'index_exp', 'indices', 'inf', 'info',
    'inner', 'insert', 'int_asbuffer', 'interp', 'intersect1d',
    'intersect1d_nu', 'inv', 'invert', 'iscomplex', 'iscomplexobj',
    'isfinite', 'isfortran', 'isinf', 'isnan', 'isneginf', 'isposinf',
    'isreal', 'isrealobj', 'isscalar', 'issctype', 'issubclass_',
    'issubdtype', 'issubsctype', 'item', 'itemset', 'iterable', 'ix_',
    'kaiser', 'kron', 'ldexp', 'left_shift', 'less', 'less_equal',
    'lexsort', 'linspace', 'load', 'loads', 'loadtxt', 'log', 'log10',
    'log1p', 'log2', 'logical_and', 'logical_not', 'logical_or',
    'logical_xor', 'logspace', 'lstsq', 'mat', 'matrix', 'max', 'maximum',
    'maximum_sctype', 'may_share_memory', 'mean', 'median', 'meshgrid',
    'mgrid', 'min', 'minimum', 'mintypecode', 'mod', 'modf', 'msort',
    'multiply', 'nan', 'nan_to_num', 'nanargmax', 'nanargmin', 'nanmax',
    'nanmin', 'nansum', 'ndenumerate', 'ndim', 'ndindex', 'negative',
    'newaxis', 'newbuffer', 'newbyteorder', 'nonzero', 'not_equal',
    'obj2sctype', 'ogrid', 'ones', 'ones_like', 'outer', 'permutation',
    'piecewise', 'pinv', 'pkgload', 'place', 'poisson', 'poly', 'poly1d',
    'polyadd', 'polyder', 'polydiv', 'polyfit', 'polyint', 'polymul',
    'polysub', 'polyval', 'power', 'prod', 'product', 'ptp', 'put',
    'putmask', 'r_', 'randint', 'random_integers', 'random_sample', 'ranf',
    'rank', 'ravel', 'real', 'real_if_close', 'recarray', 'reciprocal',
    'reduce', 'remainder', 'repeat', 'require', 'reshape', 'resize',
    'restoredot', 'right_shift', 'rint', 'roll', 'rollaxis', 'roots',
    'rot90', 'round', 'round_', 'row_stack', 's_', 'sample', 'savetxt',
    'sctype2char', 'searchsorted', 'seed', 'select', 'set_numeric_ops',
    'set_printoptions', 'set_string_function', 'setbufsize', 'setdiff1d',
    'seterr', 'seterrcall', 'seterrobj', 'setfield', 'setflags',
    'setmember1d', 'setxor1d', 'shape', 'show_config', 'shuffle', 'sign',
    'signbit', 'sin', 'sinc', 'sinh', 'size', 'slice', 'solve', 'sometrue',
    'sort', 'sort_complex', 'source', 'split', 'sqrt', 'square', 'squeeze',
    'standard_normal', 'std', 'subtract', 'sum', 'svd', 'swapaxes', 'take',
    'tan', 'tanh', 'tensordot', 'test', 'tile', 'tofile', 'tolist',
    'tostring', 'trace', 'transpose', 'trapz', 'tri', 'tril', 'trim_zeros',
    'triu', 'true_divide', 'typeDict', 'typename', 'uniform', 'union1d',
    'unique', 'unique1d', 'unravel_index', 'unwrap', 'vander', 'var',
    'vdot', 'vectorize', 'view', 'vonmises', 'vsplit', 'vstack', 'weibull',
    'where', 'who', 'zeros', 'zeros_like'}

LEXERS = {'': 'text', '.py': 'python', '.pxd': 'cython', '.pyx': 'cython', '.pxi':
    'pyrex'}

TERMINAL_COLORS = {Token: ('', ''), Whitespace: ('gray', 'brightblack'), Comment: ('gray',
    'brightblack'), Comment.Preproc: ('cyan', 'brightcyan'), Keyword: (
    'blue', 'brightblue'), Keyword.Type: ('cyan', 'brightcyan'), Operator.
    Word: ('magenta', 'brightmagenta'), Name.Builtin: ('cyan', 'brightcyan'
    ), Name.Function: ('green', 'brightgreen'), Name.Namespace: ('_cyan_',
    '_brightcyan_'), Name.Class: ('_green_', '_brightgreen_'), Name.
    Exception: ('cyan', 'brightcyan'), Name.Decorator: ('brightblack',
    'gray'), Name.Variable: ('red', 'brightred'), Name.Constant: ('red',
    'brightred'), Name.Attribute: ('cyan', 'brightcyan'), Name.Tag: (
    'brightblue', 'brightblue'), String: ('yellow', 'yellow'), Number: (
    'blue', 'brightblue'), Generic.Deleted: ('brightred', 'brightred'),
    Generic.Inserted: ('green', 'brightgreen'), Generic.Heading: ('**',
    '**'), Generic.Subheading: ('*magenta*', '*brightmagenta*'), Generic.
    Prompt: ('**', '**'), Generic.Error: ('brightred', 'brightred'), Error:
    ('_brightred_', '_brightred_')}

CSSFILE_TEMPLATE = """/*
generated by Pygments <https://pygments.org/>
Copyright 2006-2024 by the Pygments team.
Licensed under the BSD license, see LICENSE for details.
*/
%(styledefs)s
"""

DOC_HEADER = (
    """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">
<!--
generated by Pygments <https://pygments.org/>
Copyright 2006-2024 by the Pygments team.
Licensed under the BSD license, see LICENSE for details.
-->
<html>
<head>
  <title>%(title)s</title>
  <meta http-equiv="content-type" content="text/html; charset=%(encoding)s">
  <style type="text/css">
"""
     + CSSFILE_TEMPLATE + """
  </style>
</head>
<body>
<h2>%(title)s</h2>

"""
    )

DOC_HEADER_EXTERNALCSS = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN"
   "http://www.w3.org/TR/html4/strict.dtd">

<html>
<head>
  <title>%(title)s</title>
  <meta http-equiv="content-type" content="text/html; charset=%(encoding)s">
  <link rel="stylesheet" href="%(cssfile)s" type="text/css">
</head>
<body>
<h2>%(title)s</h2>

"""

DOC_FOOTER = """</body>
</html>
"""

IRC_COLORS = {Token: ('', ''), Whitespace: ('gray', 'brightblack'), Comment: ('gray',
    'brightblack'), Comment.Preproc: ('cyan', 'brightcyan'), Keyword: (
    'blue', 'brightblue'), Keyword.Type: ('cyan', 'brightcyan'), Operator.
    Word: ('magenta', 'brightcyan'), Name.Builtin: ('cyan', 'brightcyan'),
    Name.Function: ('green', 'brightgreen'), Name.Namespace: ('_cyan_',
    '_brightcyan_'), Name.Class: ('_green_', '_brightgreen_'), Name.
    Exception: ('cyan', 'brightcyan'), Name.Decorator: ('brightblack',
    'gray'), Name.Variable: ('red', 'brightred'), Name.Constant: ('red',
    'brightred'), Name.Attribute: ('cyan', 'brightcyan'), Name.Tag: (
    'brightblue', 'brightblue'), String: ('yellow', 'yellow'), Number: (
    'blue', 'brightblue'), Generic.Deleted: ('brightred', 'brightred'),
    Generic.Inserted: ('green', 'brightgreen'), Generic.Heading: ('**',
    '**'), Generic.Subheading: ('*magenta*', '*brightmagenta*'), Generic.
    Error: ('brightred', 'brightred'), Error: ('_brightred_', '_brightred_')}

IRC_COLOR_MAP = {'white': 0, 'black': 1, 'blue': 2, 'brightgreen': 3, 'brightred': 4,
    'yellow': 5, 'magenta': 6, 'orange': 7, 'green': 7, 'brightyellow': 8,
    'lightgreen': 9, 'brightcyan': 9, 'cyan': 10, 'lightblue': 11, 'red': 
    11, 'brightblue': 12, 'brightmagenta': 13, 'brightblack': 14, 'gray': 15}

TESTCASE_BEFORE = """    def testNeedsName(lexer):
        fragment = %r
        tokens = [
"""

TESTCASE_AFTER = """        ]
        assert list(lexer.get_tokens(fragment)) == tokens
"""

STYLES = {'AbapStyle': ('pygments.styles.abap', 'abap', ()), 'AlgolStyle': (
    'pygments.styles.algol', 'algol', ()), 'Algol_NuStyle': (
    'pygments.styles.algol_nu', 'algol_nu', ()), 'ArduinoStyle': (
    'pygments.styles.arduino', 'arduino', ()), 'AutumnStyle': (
    'pygments.styles.autumn', 'autumn', ()), 'BlackWhiteStyle': (
    'pygments.styles.bw', 'bw', ()), 'BorlandStyle': (
    'pygments.styles.borland', 'borland', ()), 'CoffeeStyle': (
    'pygments.styles.coffee', 'coffee', ()), 'ColorfulStyle': (
    'pygments.styles.colorful', 'colorful', ()), 'DefaultStyle': (
    'pygments.styles.default', 'default', ()), 'DraculaStyle': (
    'pygments.styles.dracula', 'dracula', ()), 'EmacsStyle': (
    'pygments.styles.emacs', 'emacs', ()), 'FriendlyGrayscaleStyle': (
    'pygments.styles.friendly_grayscale', 'friendly_grayscale', ()),
    'FriendlyStyle': ('pygments.styles.friendly', 'friendly', ()),
    'FruityStyle': ('pygments.styles.fruity', 'fruity', ()), 'GhDarkStyle':
    ('pygments.styles.gh_dark', 'github-dark', ()), 'GruvboxDarkStyle': (
    'pygments.styles.gruvbox', 'gruvbox-dark', ()), 'GruvboxLightStyle': (
    'pygments.styles.gruvbox', 'gruvbox-light', ()), 'IgorStyle': (
    'pygments.styles.igor', 'igor', ()), 'InkPotStyle': (
    'pygments.styles.inkpot', 'inkpot', ()), 'LightbulbStyle': (
    'pygments.styles.lightbulb', 'lightbulb', ()), 'LilyPondStyle': (
    'pygments.styles.lilypond', 'lilypond', ()), 'LovelaceStyle': (
    'pygments.styles.lovelace', 'lovelace', ()), 'ManniStyle': (
    'pygments.styles.manni', 'manni', ()), 'MaterialStyle': (
    'pygments.styles.material', 'material', ()), 'MonokaiStyle': (
    'pygments.styles.monokai', 'monokai', ()), 'MurphyStyle': (
    'pygments.styles.murphy', 'murphy', ()), 'NativeStyle': (
    'pygments.styles.native', 'native', ()), 'NordDarkerStyle': (
    'pygments.styles.nord', 'nord-darker', ()), 'NordStyle': (
    'pygments.styles.nord', 'nord', ()), 'OneDarkStyle': (
    'pygments.styles.onedark', 'one-dark', ()), 'ParaisoDarkStyle': (
    'pygments.styles.paraiso_dark', 'paraiso-dark', ()),
    'ParaisoLightStyle': ('pygments.styles.paraiso_light', 'paraiso-light',
    ()), 'PastieStyle': ('pygments.styles.pastie', 'pastie', ()),
    'PerldocStyle': ('pygments.styles.perldoc', 'perldoc', ()),
    'RainbowDashStyle': ('pygments.styles.rainbow_dash', 'rainbow_dash', ()
    ), 'RrtStyle': ('pygments.styles.rrt', 'rrt', ()), 'SasStyle': (
    'pygments.styles.sas', 'sas', ()), 'SolarizedDarkStyle': (
    'pygments.styles.solarized', 'solarized-dark', ()),
    'SolarizedLightStyle': ('pygments.styles.solarized', 'solarized-light',
    ()), 'StarofficeStyle': ('pygments.styles.staroffice', 'staroffice', ()
    ), 'StataDarkStyle': ('pygments.styles.stata_dark', 'stata-dark', ()),
    'StataLightStyle': ('pygments.styles.stata_light', 'stata-light', ()),
    'TangoStyle': ('pygments.styles.tango', 'tango', ()), 'TracStyle': (
    'pygments.styles.trac', 'trac', ()), 'VimStyle': ('pygments.styles.vim',
    'vim', ()), 'VisualStudioStyle': ('pygments.styles.vs', 'vs', ()),
    'XcodeStyle': ('pygments.styles.xcode', 'xcode', ()), 'ZenburnStyle': (
    'pygments.styles.zenburn', 'zenburn', ())}

DEFAULT_FONT_NAME_NIX = """DejaVu Sans Mono"""

DEFAULT_FONT_NAME_WIN = """Courier New"""

DEFAULT_FONT_NAME_MAC = """Menlo"""

FORMATTERS = {'BBCodeFormatter': ('pygments.formatters.bbcode', 'BBCode', ('bbcode',
    'bb'), (),
    'Format tokens with BBcodes. These formatting codes are used by many bulletin boards, so you can highlight your sourcecode with pygments before posting it there.'
    ), 'BmpImageFormatter': ('pygments.formatters.img', 'img_bmp', ('bmp',
    'bitmap'), ('*.bmp',),
    'Create a bitmap image from source code. This uses the Python Imaging Library to generate a pixmap from the source code.'
    ), 'GifImageFormatter': ('pygments.formatters.img', 'img_gif', ('gif',),
    ('*.gif',),
    'Create a GIF image from source code. This uses the Python Imaging Library to generate a pixmap from the source code.'
    ), 'GroffFormatter': ('pygments.formatters.groff', 'groff', ('groff',
    'troff', 'roff'), (),
    'Format tokens with groff escapes to change their color and font style.'
    ), 'HtmlFormatter': ('pygments.formatters.html', 'HTML', ('html',), (
    '*.html', '*.htm'),
    "Format tokens as HTML 4 ``<span>`` tags. By default, the content is enclosed in a ``<pre>`` tag, itself wrapped in a ``<div>`` tag (but see the `nowrap` option). The ``<div>``'s CSS class can be set by the `cssclass` option."
    ), 'IRCFormatter': ('pygments.formatters.irc', 'IRC', ('irc', 'IRC'), (
    ), 'Format tokens with IRC color sequences'), 'ImageFormatter': (
    'pygments.formatters.img', 'img', ('img', 'IMG', 'png'), ('*.png',),
    'Create a PNG image from source code. This uses the Python Imaging Library to generate a pixmap from the source code.'
    ), 'JpgImageFormatter': ('pygments.formatters.img', 'img_jpg', ('jpg',
    'jpeg'), ('*.jpg',),
    'Create a JPEG image from source code. This uses the Python Imaging Library to generate a pixmap from the source code.'
    ), 'LatexFormatter': ('pygments.formatters.latex', 'LaTeX', ('latex',
    'tex'), ('*.tex',),
    'Format tokens as LaTeX code. This needs the `fancyvrb` and `color` standard packages.'
    ), 'NullFormatter': ('pygments.formatters.other', 'Text only', ('text',
    'null'), ('*.txt',),
    'Output the text unchanged without any formatting.'),
    'PangoMarkupFormatter': ('pygments.formatters.pangomarkup',
    'Pango Markup', ('pango', 'pangomarkup'), (),
    'Format tokens as Pango Markup code. It can then be rendered to an SVG.'
    ), 'RawTokenFormatter': ('pygments.formatters.other', 'Raw tokens', (
    'raw', 'tokens'), ('*.raw',),
    'Format tokens as a raw representation for storing token streams.'),
    'RtfFormatter': ('pygments.formatters.rtf', 'RTF', ('rtf',), ('*.rtf',),
    'Format tokens as RTF markup. This formatter automatically outputs full RTF documents with color information and other useful stuff. Perfect for Copy and Paste into Microsoft(R) Word(R) documents.'
    ), 'SvgFormatter': ('pygments.formatters.svg', 'SVG', ('svg',), (
    '*.svg',),
    'Format tokens as an SVG graphics file.  This formatter is still experimental. Each line of code is a ``<text>`` element with explicit ``x`` and ``y`` coordinates containing ``<tspan>`` elements with the individual token styles.'
    ), 'Terminal256Formatter': ('pygments.formatters.terminal256',
    'Terminal256', ('terminal256', 'console256', '256'), (),
    'Format tokens with ANSI color sequences, for output in a 256-color terminal or console.  Like in `TerminalFormatter` color sequences are terminated at newlines, so that paging the output works correctly.'
    ), 'TerminalFormatter': ('pygments.formatters.terminal', 'Terminal', (
    'terminal', 'console'), (),
    'Format tokens with ANSI color sequences, for output in a text console. Color sequences are terminated at newlines, so that paging the output works correctly.'
    ), 'TerminalTrueColorFormatter': ('pygments.formatters.terminal256',
    'TerminalTrueColor', ('terminal16m', 'console16m', '16m'), (),
    'Format tokens with ANSI color sequences, for output in a true-color terminal or console.  Like in `TerminalFormatter` color sequences are terminated at newlines, so that paging the output works correctly.'
    ), 'TestcaseFormatter': ('pygments.formatters.other', 'Testcase', (
    'testcase',), (), 'Format tokens as appropriate for a new testcase.')}

DOC_TEMPLATE = """
\\documentclass{%(docclass)s}
\\usepackage{fancyvrb}
\\usepackage{color}
\\usepackage[%(encoding)s]{inputenc}
%(preamble)s

%(styledefs)s

\\begin{document}

\\section*{%(title)s}

%(code)s
\\end{document}
"""

STYLE_TEMPLATE = """
\\makeatletter
\\def\\%(cp)s@reset{\\let\\%(cp)s@it=\\relax \\let\\%(cp)s@bf=\\relax%%
    \\let\\%(cp)s@ul=\\relax \\let\\%(cp)s@tc=\\relax%%
    \\let\\%(cp)s@bc=\\relax \\let\\%(cp)s@ff=\\relax}
\\def\\%(cp)s@tok#1{\\csname %(cp)s@tok@#1\\endcsname}
\\def\\%(cp)s@toks#1+{\\ifx\\relax#1\\empty\\else%%
    \\%(cp)s@tok{#1}\\expandafter\\%(cp)s@toks\\fi}
\\def\\%(cp)s@do#1{\\%(cp)s@bc{\\%(cp)s@tc{\\%(cp)s@ul{%%
    \\%(cp)s@it{\\%(cp)s@bf{\\%(cp)s@ff{#1}}}}}}}
\\def\\%(cp)s#1#2{\\%(cp)s@reset\\%(cp)s@toks#1+\\relax+\\%(cp)s@do{#2}}

%(styles)s

\\def\\%(cp)sZbs{\\char`\\\\}
\\def\\%(cp)sZus{\\char`\\_}
\\def\\%(cp)sZob{\\char`\\{}
\\def\\%(cp)sZcb{\\char`\\}}
\\def\\%(cp)sZca{\\char`\\^}
\\def\\%(cp)sZam{\\char`\\&}
\\def\\%(cp)sZlt{\\char`\\<}
\\def\\%(cp)sZgt{\\char`\\>}
\\def\\%(cp)sZsh{\\char`\\#}
\\def\\%(cp)sZpc{\\char`\\%%}
\\def\\%(cp)sZdl{\\char`\\$}
\\def\\%(cp)sZhy{\\char`\\-}
\\def\\%(cp)sZsq{\\char`\\'}
\\def\\%(cp)sZdq{\\char`\\"}
\\def\\%(cp)sZti{\\char`\\~}
%% for compatibility with earlier versions
\\def\\%(cp)sZat{@}
\\def\\%(cp)sZlb{[}
\\def\\%(cp)sZrb{]}
\\makeatother
"""

STYLE_MAP = {v[1]: (v[0].split('.')[-1] + '::' + k) for k, v in STYLES.items()}

_STYLE_NAME_TO_MODULE_MAP = {v[1]: (v[0], k) for k, v in STYLES.items()}

HASHER_HASH = re.compile('^(\\w+)=([a-f0-9]+)')

CHARSET = re.compile(';\\s*charset\\s*=\\s*(.*)\\s*$', re.I)

HTML_CONTENT_TYPE = re.compile('text/html|application/x(ht)?ml')

DEFAULT_INDEX = """https://pypi.org/pypi"""

PKG_INFO_ENCODING = """utf-8"""

PKG_INFO_PREFERRED_VERSION = """1.1"""

_LINE_PREFIX_1_2 = re.compile('\n       \\|')

_LINE_PREFIX_PRE_1_2 = re.compile('\n        ')

_241_FIELDS = ('Metadata-Version', 'Name', 'Version', 'Platform', 'Summary',
    'Description', 'Keywords', 'Home-page', 'Author', 'Author-email', 'License'
    )

_314_FIELDS = ('Metadata-Version', 'Name', 'Version', 'Platform', 'Supported-Platform',
    'Summary', 'Description', 'Keywords', 'Home-page', 'Author',
    'Author-email', 'License', 'Classifier', 'Download-URL', 'Obsoletes',
    'Provides', 'Requires')

_314_MARKERS = ('Obsoletes', 'Provides', 'Requires', 'Classifier', 'Download-URL')

_345_FIELDS = ('Metadata-Version', 'Name', 'Version', 'Platform', 'Supported-Platform',
    'Summary', 'Description', 'Keywords', 'Home-page', 'Author',
    'Author-email', 'Maintainer', 'Maintainer-email', 'License',
    'Classifier', 'Download-URL', 'Obsoletes-Dist', 'Project-URL',
    'Provides-Dist', 'Requires-Dist', 'Requires-Python', 'Requires-External')

_345_MARKERS = ('Provides-Dist', 'Requires-Dist', 'Requires-Python', 'Obsoletes-Dist',
    'Requires-External', 'Maintainer', 'Maintainer-email', 'Project-URL')

_426_FIELDS = ('Metadata-Version', 'Name', 'Version', 'Platform', 'Supported-Platform',
    'Summary', 'Description', 'Keywords', 'Home-page', 'Author',
    'Author-email', 'Maintainer', 'Maintainer-email', 'License',
    'Classifier', 'Download-URL', 'Obsoletes-Dist', 'Project-URL',
    'Provides-Dist', 'Requires-Dist', 'Requires-Python',
    'Requires-External', 'Private-Version', 'Obsoleted-By',
    'Setup-Requires-Dist', 'Extension', 'Provides-Extra')

_426_MARKERS = ('Private-Version', 'Provides-Extra', 'Obsoleted-By', 'Setup-Requires-Dist',
    'Extension')

_566_FIELDS = (_426_FIELDS + ('Description-Content-Type', 'Requires', 'Provides',
    'Obsoletes'))

_566_MARKERS = ('Description-Content-Type',)

_643_MARKERS = ('Dynamic', 'License-File')

_643_FIELDS = (_566_FIELDS + _643_MARKERS)

_ALL_FIELDS = set()

EXTRA_RE = re.compile('extra\\s*==\\s*("([^"]+)"|\'([^\']+)\')')

_ATTR2FIELD = {name.lower().replace('-', '_'): name for name in _ALL_FIELDS}

_FIELD2ATTR = {field: attr for attr, field in _ATTR2FIELD.items()}

_PREDICATE_FIELDS = ('Requires-Dist', 'Obsoletes-Dist', 'Provides-Dist')

_VERSIONS_FIELDS = ('Requires-Python',)

_VERSION_FIELDS = ('Version',)

_LISTFIELDS = ('Platform', 'Classifier', 'Obsoletes', 'Requires', 'Provides',
    'Obsoletes-Dist', 'Provides-Dist', 'Requires-Dist', 'Requires-External',
    'Project-URL', 'Supported-Platform', 'Setup-Requires-Dist',
    'Provides-Extra', 'Extension', 'License-File')

_LISTTUPLEFIELDS = ('Project-URL',)

_ELEMENTSFIELD = ('Keywords',)

_UNICODEFIELDS = ('Author', 'Maintainer', 'Summary', 'Description')

_MISSING = object()

_FILESAFE = re.compile('[^A-Za-z0-9.]+')

METADATA_FILENAME = """pydist.json"""

WHEEL_METADATA_FILENAME = """metadata.json"""

LEGACY_METADATA_FILENAME = """METADATA"""

METADATA_VERSION_MATCHER = re.compile('^\\d+(\\.\\d+)*$')

NAME_MATCHER = re.compile('^[0-9A-Z]([0-9A-Z_.-]*[0-9A-Z])?$', re.I)

FIELDNAME_MATCHER = re.compile('^[A-Z]([0-9A-Z-]*[0-9A-Z])?$', re.I)

VERSION_MATCHER = PEP440_VERSION_RE

SUMMARY_MATCHER = re.compile('.{1,2047}')

METADATA_VERSION = """2.0"""

GENERATOR = ('distlib (%s)' % __version__)

MANDATORY_KEYS = {'name': (), 'version': (), 'summary': ('legacy',)}

INDEX_KEYS = """name version license summary description author author_email keywords platform home_page classifiers download_url"""

DEPENDENCY_KEYS = """extras run_requires test_requires build_requires dev_requires provides meta_requires obsoleted_by supports_environments"""

SYNTAX_VALIDATORS = {'metadata_version': (METADATA_VERSION_MATCHER, ()), 'name': (NAME_MATCHER,
    ('legacy',)), 'version': (VERSION_MATCHER, ('legacy',)), 'summary': (
    SUMMARY_MATCHER, ('legacy',)), 'dynamic': (FIELDNAME_MATCHER, ('legacy',))}

LEGACY_MAPPING = {'name': 'Name', 'version': 'Version', ('extensions', 'python.details',
    'license'): 'License', 'summary': 'Summary', 'description':
    'Description', ('extensions', 'python.project', 'project_urls', 'Home'):
    'Home-page', ('extensions', 'python.project', 'contacts', 0, 'name'):
    'Author', ('extensions', 'python.project', 'contacts', 0, 'email'):
    'Author-email', 'source_url': 'Download-URL', ('extensions',
    'python.details', 'classifiers'): 'Classifier'}

PEP440_VERSION_RE = re.compile(
    '^v?(\\d+!)?(\\d+(\\.\\d+)*)((a|alpha|b|beta|c|rc|pre|preview)(\\d+)?)?(\\.(post|r|rev)(\\d+)?)?([._-]?(dev)(\\d+)?)?(\\+([a-zA-Z\\d]+(\\.[a-zA-Z\\d]+)?))?$'
    , re.I)

PREREL_TAGS = set(['a', 'b', 'c', 'rc', 'dev'])

_REPLACEMENTS = ((re.compile('[.+-]$'), ''), (re.compile('^[.](\\d)'), '0.\\1'), (re.
    compile('^[.-]'), ''), (re.compile('^\\((.*)\\)$'), '\\1'), (re.compile
    ('^v(ersion)?\\s*(\\d+)'), '\\2'), (re.compile('^r(ev)?\\s*(\\d+)'),
    '\\2'), (re.compile('[.]{2,}'), '.'), (re.compile('\\b(alfa|apha)\\b'),
    'alpha'), (re.compile('\\b(pre-alpha|prealpha)\\b'), 'pre.alpha'), (re.
    compile('\\(beta\\)$'), 'beta'))

_SUFFIX_REPLACEMENTS = ((re.compile('^[:~._+-]+'), ''), (re.compile('[,*")([\\]]'), ''), (re.
    compile('[~:+_ -]'), '.'), (re.compile('[.]{2,}'), '.'), (re.compile(
    '\\.$'), ''))

_NUMERIC_PREFIX = re.compile('(\\d+(\\.\\d+)*)')

_VERSION_PART = re.compile('([a-z]+|\\d+|[\\.-])', re.I)

_VERSION_REPLACE = {'pre': 'c', 'preview': 'c', '-': 'final-', 'rc': 'c', 'dev': '@', '': None,
    '.': None}

_SEMVER_RE = re.compile(
    '^(\\d+)\\.(\\d+)\\.(\\d+)(-[a-z0-9]+(\\.[a-z0-9-]+)*)?(\\+[a-z0-9]+(\\.[a-z0-9-]+)*)?$'
    , re.I)

_SCHEMES = {'normalized': VersionScheme(_normalized_key, NormalizedMatcher,
    _suggest_normalized_version), 'legacy': VersionScheme(_legacy_key,
    LegacyMatcher, lambda self, s: s), 'semantic': VersionScheme(
    _semantic_key, SemanticMatcher, _suggest_semantic_version)}

IDENTIFIER = re.compile('^([\\w\\.-]+)\\s*')

CONVERT_PATTERN = re.compile('^(?P<prefix>[a-z]+)://(?P<suffix>.*)$')

WORD_PATTERN = re.compile('^\\s*(\\w+)\\s*')

DOT_PATTERN = re.compile('^\\.\\s*(\\w+)\\s*')

INDEX_PATTERN = re.compile('^\\[\\s*(\\w+)\\s*\\]\\s*')

DIGIT_PATTERN = re.compile('^\\d+$')

DEFAULT_REALM = """pypi"""

_COLLAPSE_PATTERN = re.compile('\\\\w*\n', re.M)

_COMMENTED_LINE = re.compile("""#.*?(?=
)|
(?=$)""", re.M | re.S)

_PYTHON_VERSION = sys.version_info[:2]

VERSION_IDENTIFIER = re.compile('^([\\w\\.*+-]+)\\s*')

COMPARE_OP = re.compile('^(<=?|>=?|={2,3}|[~!]=)\\s*')

MARKER_OP = re.compile('^((<=?)|(>=?)|={2,3}|[~!]=|in|not\\s+in)\\s*')

OR = re.compile('^or\\b\\s*')

AND = re.compile('^and\\b\\s*')

NON_SPACE = re.compile('(\\S+)\\s*')

STRING_CHUNK = re.compile('([\\s\\w\\.{}()*+#:;,/?!~`@$%^&=|<>\\[\\]-]+)')

ENTRY_RE = re.compile(
    """(?P<name>([^\\[]\\S*))
                      \\s*=\\s*(?P<callable>(\\w+)([:\\.]\\w+)*)
                      \\s*(\\[\\s*(?P<flags>[\\w-]+(=\\w+)?(,\\s*\\w+(=\\w+)?)*)\\s*\\])?
                      """
    , re.VERBOSE)

PROJECT_NAME_AND_VERSION = re.compile('([a-z0-9_]+([.-][a-z_][a-z0-9_]*)*)-([a-z0-9_.+-]+)', re.I)

PYTHON_VERSION = re.compile('-py(\\d\\.?\\d?)')

NAME_VERSION_RE = re.compile("""
(?P<nm>[^-]+)
-(?P<vn>\\d+[^-]*)
(-(?P<bn>\\d+[^-]*))?$
""",
    re.IGNORECASE | re.VERBOSE)

UNITS = ('', 'K', 'M', 'G', 'T', 'P')

RICH_GLOB = re.compile('\\{([^}]*)\\}')

_CHECK_RECURSIVE_GLOB = re.compile('[^/\\\\,{]\\*\\*|\\*\\*[^/\\\\,}]')

_CHECK_MISMATCH_SET = re.compile('^[^{]*\\}|\\{[^}]*$')

DEFAULT_REPOSITORY = """https://upload.pypi.org/legacy/"""

_TARGET_TO_PLAT = {'x86': 'win32', 'x64': 'win-amd64', 'arm': 'win-arm32'}

EXPORTS_FILENAME = """pydist-exports.json"""

COMMANDS_FILENAME = """pydist-commands.json"""

DIST_FILES = ('INSTALLER', METADATA_FILENAME, 'RECORD', 'REQUESTED', 'RESOURCES',
    EXPORTS_FILENAME, 'SHARED')

DISTINFO_EXT = """.dist-info"""

_VERSION_MARKERS = {'python_version', 'python_full_version'}

_DIGITS = re.compile('\\d+\\.\\d+')

DEFAULT_CONTEXT = default_context()

_DEFAULT_MANIFEST = """
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
 <assemblyIdentity version="1.0.0.0"
 processorArchitecture="X86"
 name="%s"
 type="win32"/>

 <!-- Identify the application security requirements. -->
 <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
 <security>
 <requestedPrivileges>
 <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
 </requestedPrivileges>
 </security>
 </trustInfo>
</assembly>""".strip(
    )

FIRST_LINE_RE = re.compile(b'^#!.*pythonw?[0-9.]*([ \t].*)?$')

SCRIPT_TEMPLATE = """# -*- coding: utf-8 -*-
import re
import sys
from %(module)s import %(import_name)s
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\\.pyw|\\.exe)?$', '', sys.argv[0])
    sys.exit(%(func)s())
"""

DISTLIB_PACKAGE = __name__.rsplit('.', 1)[0]

WRAPPERS = {r.name: r.bytes for r in finder(DISTLIB_PACKAGE).iterator('') if r.name.
    endswith('.exe')}

IMP_PREFIX = """cp"""

VER_SUFFIX = ('%s%s' % sys.version_info[:2])

PYVER = ('py' + VER_SUFFIX)

IMPVER = (IMP_PREFIX + VER_SUFFIX)

ARCH = get_platform().replace('-', '_').replace('.', '_')

ABI = _derive_abi()

FILENAME_RE = re.compile(
    """
(?P<nm>[^-]+)
-(?P<vn>\\d+[^-]*)
(-(?P<bn>\\d+[^-]*))?
-(?P<py>\\w+\\d+(\\.\\w+\\d+)*)
-(?P<bi>\\w+)
-(?P<ar>\\w+(\\.\\w+)*)
\\.whl$
"""
    , re.IGNORECASE | re.VERBOSE)

SHEBANG_RE = re.compile(b'\\s*#![^\\r\\n]*')

SHEBANG_DETAIL_RE = re.compile(b'^(\\s*#!("[^"]+"|\\S+))\\s+(.*)$')

SHEBANG_PYTHON = b'#!python'

SHEBANG_PYTHONW = b'#!pythonw'

COMPATIBLE_TAGS = compatible_tags()

_UNIXCONFDIR = os.environ.get('UNIXCONFDIR', '/etc')

_UNIXUSRLIBDIR = os.environ.get('UNIXUSRLIBDIR', '/usr/lib')

_OS_RELEASE_BASENAME = """os-release"""

NORMALIZED_OS_ID = {'ol': 'oracle', 'opensuse-leap': 'opensuse'}

NORMALIZED_LSB_ID = {'enterpriseenterpriseas': 'oracle', 'enterpriseenterpriseserver': 'oracle',
    'redhatenterpriseworkstation': 'rhel', 'redhatenterpriseserver': 'rhel',
    'redhatenterprisecomputenode': 'rhel'}

NORMALIZED_DISTRO_ID = {'redhat': 'rhel'}

_DISTRO_RELEASE_CONTENT_REVERSED_PATTERN = re.compile(
    '(?:[^)]*\\)(.*)\\()? *(?:STL )?([\\d.+\\-a-z]*\\d) *(?:esaeler *)?(.+)')

_DISTRO_RELEASE_BASENAME_PATTERN = re.compile('(\\w+)[-_](release|version)$')

_DISTRO_RELEASE_BASENAMES = ['SuSE-release', 'altlinux-release', 'arch-release', 'base-release',
    'centos-release', 'fedora-release', 'gentoo-release', 'mageia-release',
    'mandrake-release', 'mandriva-release', 'mandrivalinux-release',
    'manjaro-release', 'oracle-release', 'redhat-release', 'rocky-release',
    'sl-release', 'slackware-version']

_DISTRO_RELEASE_IGNORE_BASENAMES = ('debian_version', 'lsb-release', 'oem-release', _OS_RELEASE_BASENAME,
    'system-release', 'plesk-release', 'iredmail-release', 'board-release',
    'ec2_version')

URI = re.compile('^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\\?([^#]*))?(#(.*))?')

PERMANENT_REDIRECT_STATUSES = (301, 308)

TIME_FMT = """%a, %d %b %Y %H:%M:%S GMT"""

CONTENT_TYPE_FORM_URLENCODED = """application/x-www-form-urlencoded"""

CONTENT_TYPE_MULTI_PART = """multipart/form-data"""

KD = (lambda s, d: hash_utf8(f'{s}:{d}'))

HA1 = hash_utf8(f'{HA1}:{nonce}:{cnonce}')

HA2 = hash_utf8(A2)

HOOKS = ['response']

REDIRECT_STATI = (codes.moved, codes.found, codes.other, codes.temporary_redirect, codes.
    permanent_redirect)

DEFAULT_REDIRECT_LIMIT = (30)

CONTENT_CHUNK_SIZE = (10 * 1024)

ITER_CHUNK_SIZE = (512)

_VALID_HEADER_NAME_RE_BYTE = re.compile(b'^[^:\\s][^:\\r\\n]*$')

_VALID_HEADER_NAME_RE_STR = re.compile('^[^:\\s][^:\\r\\n]*$')

_VALID_HEADER_VALUE_RE_BYTE = re.compile(b'^\\S[^\\r\\n]*$|^$')

_VALID_HEADER_VALUE_RE_STR = re.compile('^\\S[^\\r\\n]*$|^$')

_HEADER_VALIDATORS_STR = (_VALID_HEADER_NAME_RE_STR, _VALID_HEADER_VALUE_RE_STR)

_HEADER_VALIDATORS_BYTE = (_VALID_HEADER_NAME_RE_BYTE, _VALID_HEADER_VALUE_RE_BYTE)

HEADER_VALIDATORS = {bytes: _HEADER_VALIDATORS_BYTE, str: _HEADER_VALIDATORS_STR}

NETRC_FILES = ('.netrc', '_netrc')

DEFAULT_CA_BUNDLE_PATH = certs.where()

DEFAULT_PORTS = {'http': 80, 'https': 443}

DEFAULT_ACCEPT_ENCODING = """, """.join(re.split(',\\s*', make_headers(accept_encoding=True)[
    'accept-encoding']))

UNRESERVED_SET = frozenset('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' +
    '0123456789-._~')

DEFAULT_POOLBLOCK = (False)

DEFAULT_POOLSIZE = (10)

DEFAULT_RETRIES = (0)

DEFAULT_POOL_TIMEOUT = None

ASCII_CTRL = (frozenset(chr(i) for i in range(32)) | frozenset(chr(127)))

ILLEGAL_BASIC_STR_CHARS = (ASCII_CTRL - frozenset('\t'))

ILLEGAL_MULTILINE_BASIC_STR_CHARS = (ASCII_CTRL - frozenset('\t\n'))

ILLEGAL_LITERAL_STR_CHARS = ILLEGAL_BASIC_STR_CHARS

ILLEGAL_MULTILINE_LITERAL_STR_CHARS = ILLEGAL_MULTILINE_BASIC_STR_CHARS

ILLEGAL_COMMENT_CHARS = ILLEGAL_BASIC_STR_CHARS

TOML_WS = frozenset(' \t')

TOML_WS_AND_NEWLINE = (TOML_WS | frozenset('\n'))

BARE_KEY_CHARS = frozenset(string.ascii_letters + string.digits + '-_')

KEY_INITIAL_CHARS = (BARE_KEY_CHARS | frozenset('"\''))

HEXDIGIT_CHARS = frozenset(string.hexdigits)

BASIC_STR_ESCAPE_REPLACEMENTS = MappingProxyType({'\\b': '\x08', '\\t': '\t', '\\n': '\n', '\\f': '\x0c',
    '\\r': '\r', '\\"': '"', '\\\\': '\\'})

FROZEN = (0)

EXPLICIT_NEST = (1)

_TIME_RE_STR = """([01][0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])(?:\\.([0-9]{1,6})[0-9]*)?"""

RE_NUMBER = re.compile(
    """
0
(?:
    x[0-9A-Fa-f](?:_?[0-9A-Fa-f])*   # hex
    |
    b[01](?:_?[01])*                 # bin
    |
    o[0-7](?:_?[0-7])*               # oct
)
|
[+-]?(?:0|[1-9](?:_?[0-9])*)         # dec, integer part
(?P<floatpart>
    (?:\\.[0-9](?:_?[0-9])*)?         # optional fractional part
    (?:[eE][+-]?[0-9](?:_?[0-9])*)?  # optional exponent part
)
"""
    , flags=re.VERBOSE)

RE_LOCALTIME = re.compile(_TIME_RE_STR)

RE_DATETIME = re.compile(
    f"""
([0-9]{{4}})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])  # date, e.g. 1988-10-27
(?:
    [Tt ]
    {_TIME_RE_STR}
    (?:([Zz])|([+-])([01][0-9]|2[0-3]):([0-5][0-9]))?  # optional time offset
)?
"""
    , flags=re.VERBOSE)

_CACERT_CTX = get_path('pip._vendor.certifi', 'cacert.pem')

_CACERT_PATH = str(_CACERT_CTX.__enter__())

WHEEL_BUILT_MARKER = """PEP517_ALREADY_BUILT_WHEEL"""

HOOK_NAMES = {'get_requires_for_build_wheel', 'prepare_metadata_for_build_wheel',
    'build_wheel', 'get_requires_for_build_editable',
    'prepare_metadata_for_build_editable', 'build_editable',
    'get_requires_for_build_sdist', 'build_sdist', '_supported_features'}

DEFAULT = (0)

FORMAT = """%(message)s"""

ASCII_GUIDES = ('    ', '|   ', '+-- ', '`-- ')

TREE_GUIDES = [('    ', '│   ', '├── ', '└── '), ('    ', '┃   ', '┣━━ ', '┗━━ '), (
    '    ', '║   ', '╠══ ', '╚══ ')]

JUPYTER_DEFAULT_COLUMNS = (115)

JUPYTER_DEFAULT_LINES = (100)

NO_CHANGE = NoChange()

_STDIN_FILENO = (0)

_STDOUT_FILENO = (1)

_STDERR_FILENO = (2)

_STD_STREAMS = (_STDIN_FILENO, _STDOUT_FILENO, _STDERR_FILENO)

_STD_STREAMS_OUTPUT = (_STDOUT_FILENO, _STDERR_FILENO)

_TERM_COLORS = {'kitty': ColorSystem.EIGHT_BIT, '256color': ColorSystem.EIGHT_BIT,
    '16color': ColorSystem.STANDARD}

COLOR_SYSTEMS = {'standard': ColorSystem.STANDARD, '256': ColorSystem.EIGHT_BIT,
    'truecolor': ColorSystem.TRUECOLOR, 'windows': ColorSystem.WINDOWS}

_COLOR_SYSTEMS_NAMES = {system: name for name, system in COLOR_SYSTEMS.items()}

MAX_WRITE = (32 * 1024 // 4)

EMOJI = {'1st_place_medal': '🥇', '2nd_place_medal': '🥈', '3rd_place_medal': '🥉',
    'ab_button_(blood_type)': '🆎', 'atm_sign': '🏧', 'a_button_(blood_type)':
    '🅰', 'afghanistan': '🇦🇫', 'albania': '🇦🇱', 'algeria': '🇩🇿',
    'american_samoa': '🇦🇸', 'andorra': '🇦🇩', 'angola': '🇦🇴', 'anguilla':
    '🇦🇮', 'antarctica': '🇦🇶', 'antigua_&_barbuda': '🇦🇬', 'aquarius': '♒',
    'argentina': '🇦🇷', 'aries': '♈', 'armenia': '🇦🇲', 'aruba': '🇦🇼',
    'ascension_island': '🇦🇨', 'australia': '🇦🇺', 'austria': '🇦🇹',
    'azerbaijan': '🇦🇿', 'back_arrow': '🔙', 'b_button_(blood_type)': '🅱',
    'bahamas': '🇧🇸', 'bahrain': '🇧🇭', 'bangladesh': '🇧🇩', 'barbados': '🇧🇧',
    'belarus': '🇧🇾', 'belgium': '🇧🇪', 'belize': '🇧🇿', 'benin': '🇧🇯',
    'bermuda': '🇧🇲', 'bhutan': '🇧🇹', 'bolivia': '🇧🇴',
    'bosnia_&_herzegovina': '🇧🇦', 'botswana': '🇧🇼', 'bouvet_island': '🇧🇻',
    'brazil': '🇧🇷', 'british_indian_ocean_territory': '🇮🇴',
    'british_virgin_islands': '🇻🇬', 'brunei': '🇧🇳', 'bulgaria': '🇧🇬',
    'burkina_faso': '🇧🇫', 'burundi': '🇧🇮', 'cl_button': '🆑', 'cool_button':
    '🆒', 'cambodia': '🇰🇭', 'cameroon': '🇨🇲', 'canada': '🇨🇦',
    'canary_islands': '🇮🇨', 'cancer': '♋', 'cape_verde': '🇨🇻', 'capricorn':
    '♑', 'caribbean_netherlands': '🇧🇶', 'cayman_islands': '🇰🇾',
    'central_african_republic': '🇨🇫', 'ceuta_&_melilla': '🇪🇦', 'chad': '🇹🇩',
    'chile': '🇨🇱', 'china': '🇨🇳', 'christmas_island': '🇨🇽',
    'christmas_tree': '🎄', 'clipperton_island': '🇨🇵',
    'cocos_(keeling)_islands': '🇨🇨', 'colombia': '🇨🇴', 'comoros': '🇰🇲',
    'congo_-_brazzaville': '🇨🇬', 'congo_-_kinshasa': '🇨🇩', 'cook_islands':
    '🇨🇰', 'costa_rica': '🇨🇷', 'croatia': '🇭🇷', 'cuba': '🇨🇺', 'curaçao':
    '🇨🇼', 'cyprus': '🇨🇾', 'czechia': '🇨🇿', 'côte_d’ivoire': '🇨🇮', 'denmark':
    '🇩🇰', 'diego_garcia': '🇩🇬', 'djibouti': '🇩🇯', 'dominica': '🇩🇲',
    'dominican_republic': '🇩🇴', 'end_arrow': '🔚', 'ecuador': '🇪🇨', 'egypt':
    '🇪🇬', 'el_salvador': '🇸🇻', 'england':
    '🏴\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f',
    'equatorial_guinea': '🇬🇶', 'eritrea': '🇪🇷', 'estonia': '🇪🇪', 'ethiopia':
    '🇪🇹', 'european_union': '🇪🇺', 'free_button': '🆓', 'falkland_islands':
    '🇫🇰', 'faroe_islands': '🇫🇴', 'fiji': '🇫🇯', 'finland': '🇫🇮', 'france':
    '🇫🇷', 'french_guiana': '🇬🇫', 'french_polynesia': '🇵🇫',
    'french_southern_territories': '🇹🇫', 'gabon': '🇬🇦', 'gambia': '🇬🇲',
    'gemini': '♊', 'georgia': '🇬🇪', 'germany': '🇩🇪', 'ghana': '🇬🇭',
    'gibraltar': '🇬🇮', 'greece': '🇬🇷', 'greenland': '🇬🇱', 'grenada': '🇬🇩',
    'guadeloupe': '🇬🇵', 'guam': '🇬🇺', 'guatemala': '🇬🇹', 'guernsey': '🇬🇬',
    'guinea': '🇬🇳', 'guinea-bissau': '🇬🇼', 'guyana': '🇬🇾', 'haiti': '🇭🇹',
    'heard_&_mcdonald_islands': '🇭🇲', 'honduras': '🇭🇳',
    'hong_kong_sar_china': '🇭🇰', 'hungary': '🇭🇺', 'id_button': '🆔',
    'iceland': '🇮🇸', 'india': '🇮🇳', 'indonesia': '🇮🇩', 'iran': '🇮🇷', 'iraq':
    '🇮🇶', 'ireland': '🇮🇪', 'isle_of_man': '🇮🇲', 'israel': '🇮🇱', 'italy':
    '🇮🇹', 'jamaica': '🇯🇲', 'japan': '🗾', 'japanese_acceptable_button': '🉑',
    'japanese_application_button': '🈸', 'japanese_bargain_button': '🉐',
    'japanese_castle': '🏯', 'japanese_congratulations_button': '㊗',
    'japanese_discount_button': '🈹', 'japanese_dolls': '🎎',
    'japanese_free_of_charge_button': '🈚', 'japanese_here_button': '🈁',
    'japanese_monthly_amount_button': '🈷', 'japanese_no_vacancy_button':
    '🈵', 'japanese_not_free_of_charge_button': '🈶',
    'japanese_open_for_business_button': '🈺',
    'japanese_passing_grade_button': '🈴', 'japanese_post_office': '🏣',
    'japanese_prohibited_button': '🈲', 'japanese_reserved_button': '🈯',
    'japanese_secret_button': '㊙', 'japanese_service_charge_button': '🈂',
    'japanese_symbol_for_beginner': '🔰', 'japanese_vacancy_button': '🈳',
    'jersey': '🇯🇪', 'jordan': '🇯🇴', 'kazakhstan': '🇰🇿', 'kenya': '🇰🇪',
    'kiribati': '🇰🇮', 'kosovo': '🇽🇰', 'kuwait': '🇰🇼', 'kyrgyzstan': '🇰🇬',
    'laos': '🇱🇦', 'latvia': '🇱🇻', 'lebanon': '🇱🇧', 'leo': '♌', 'lesotho':
    '🇱🇸', 'liberia': '🇱🇷', 'libra': '♎', 'libya': '🇱🇾', 'liechtenstein':
    '🇱🇮', 'lithuania': '🇱🇹', 'luxembourg': '🇱🇺', 'macau_sar_china': '🇲🇴',
    'macedonia': '🇲🇰', 'madagascar': '🇲🇬', 'malawi': '🇲🇼', 'malaysia': '🇲🇾',
    'maldives': '🇲🇻', 'mali': '🇲🇱', 'malta': '🇲🇹', 'marshall_islands': '🇲🇭',
    'martinique': '🇲🇶', 'mauritania': '🇲🇷', 'mauritius': '🇲🇺', 'mayotte':
    '🇾🇹', 'mexico': '🇲🇽', 'micronesia': '🇫🇲', 'moldova': '🇲🇩', 'monaco':
    '🇲🇨', 'mongolia': '🇲🇳', 'montenegro': '🇲🇪', 'montserrat': '🇲🇸',
    'morocco': '🇲🇦', 'mozambique': '🇲🇿', 'mrs._claus': '🤶',
    'mrs._claus_dark_skin_tone': '🤶🏿', 'mrs._claus_light_skin_tone': '🤶🏻',
    'mrs._claus_medium-dark_skin_tone': '🤶🏾',
    'mrs._claus_medium-light_skin_tone': '🤶🏼',
    'mrs._claus_medium_skin_tone': '🤶🏽', 'myanmar_(burma)': '🇲🇲',
    'new_button': '🆕', 'ng_button': '🆖', 'namibia': '🇳🇦', 'nauru': '🇳🇷',
    'nepal': '🇳🇵', 'netherlands': '🇳🇱', 'new_caledonia': '🇳🇨',
    'new_zealand': '🇳🇿', 'nicaragua': '🇳🇮', 'niger': '🇳🇪', 'nigeria': '🇳🇬',
    'niue': '🇳🇺', 'norfolk_island': '🇳🇫', 'north_korea': '🇰🇵',
    'northern_mariana_islands': '🇲🇵', 'norway': '🇳🇴', 'ok_button': '🆗',
    'ok_hand': '👌', 'ok_hand_dark_skin_tone': '👌🏿',
    'ok_hand_light_skin_tone': '👌🏻', 'ok_hand_medium-dark_skin_tone': '👌🏾',
    'ok_hand_medium-light_skin_tone': '👌🏼', 'ok_hand_medium_skin_tone':
    '👌🏽', 'on!_arrow': '🔛', 'o_button_(blood_type)': '🅾', 'oman': '🇴🇲',
    'ophiuchus': '⛎', 'p_button': '🅿', 'pakistan': '🇵🇰', 'palau': '🇵🇼',
    'palestinian_territories': '🇵🇸', 'panama': '🇵🇦', 'papua_new_guinea':
    '🇵🇬', 'paraguay': '🇵🇾', 'peru': '🇵🇪', 'philippines': '🇵🇭', 'pisces':
    '♓', 'pitcairn_islands': '🇵🇳', 'poland': '🇵🇱', 'portugal': '🇵🇹',
    'puerto_rico': '🇵🇷', 'qatar': '🇶🇦', 'romania': '🇷🇴', 'russia': '🇷🇺',
    'rwanda': '🇷🇼', 'réunion': '🇷🇪', 'soon_arrow': '🔜', 'sos_button': '🆘',
    'sagittarius': '♐', 'samoa': '🇼🇸', 'san_marino': '🇸🇲', 'santa_claus':
    '🎅', 'santa_claus_dark_skin_tone': '🎅🏿', 'santa_claus_light_skin_tone':
    '🎅🏻', 'santa_claus_medium-dark_skin_tone': '🎅🏾',
    'santa_claus_medium-light_skin_tone': '🎅🏼',
    'santa_claus_medium_skin_tone': '🎅🏽', 'saudi_arabia': '🇸🇦', 'scorpio':
    '♏', 'scotland':
    '🏴\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f',
    'senegal': '🇸🇳', 'serbia': '🇷🇸', 'seychelles': '🇸🇨', 'sierra_leone':
    '🇸🇱', 'singapore': '🇸🇬', 'sint_maarten': '🇸🇽', 'slovakia': '🇸🇰',
    'slovenia': '🇸🇮', 'solomon_islands': '🇸🇧', 'somalia': '🇸🇴',
    'south_africa': '🇿🇦', 'south_georgia_&_south_sandwich_islands': '🇬🇸',
    'south_korea': '🇰🇷', 'south_sudan': '🇸🇸', 'spain': '🇪🇸', 'sri_lanka':
    '🇱🇰', 'st._barthélemy': '🇧🇱', 'st._helena': '🇸🇭', 'st._kitts_&_nevis':
    '🇰🇳', 'st._lucia': '🇱🇨', 'st._martin': '🇲🇫', 'st._pierre_&_miquelon':
    '🇵🇲', 'st._vincent_&_grenadines': '🇻🇨', 'statue_of_liberty': '🗽',
    'sudan': '🇸🇩', 'suriname': '🇸🇷', 'svalbard_&_jan_mayen': '🇸🇯',
    'swaziland': '🇸🇿', 'sweden': '🇸🇪', 'switzerland': '🇨🇭', 'syria': '🇸🇾',
    'são_tomé_&_príncipe': '🇸🇹', 't-rex': '🦖', 'top_arrow': '🔝', 'taiwan':
    '🇹🇼', 'tajikistan': '🇹🇯', 'tanzania': '🇹🇿', 'taurus': '♉', 'thailand':
    '🇹🇭', 'timor-leste': '🇹🇱', 'togo': '🇹🇬', 'tokelau': '🇹🇰', 'tokyo_tower':
    '🗼', 'tonga': '🇹🇴', 'trinidad_&_tobago': '🇹🇹', 'tristan_da_cunha': '🇹🇦',
    'tunisia': '🇹🇳', 'turkey': '🦃', 'turkmenistan': '🇹🇲',
    'turks_&_caicos_islands': '🇹🇨', 'tuvalu': '🇹🇻', 'u.s._outlying_islands':
    '🇺🇲', 'u.s._virgin_islands': '🇻🇮', 'up!_button': '🆙', 'uganda': '🇺🇬',
    'ukraine': '🇺🇦', 'united_arab_emirates': '🇦🇪', 'united_kingdom': '🇬🇧',
    'united_nations': '🇺🇳', 'united_states': '🇺🇸', 'uruguay': '🇺🇾',
    'uzbekistan': '🇺🇿', 'vs_button': '🆚', 'vanuatu': '🇻🇺', 'vatican_city':
    '🇻🇦', 'venezuela': '🇻🇪', 'vietnam': '🇻🇳', 'virgo': '♍', 'wales':
    '🏴\U000e0067\U000e0062\U000e0077\U000e006c\U000e0073\U000e007f',
    'wallis_&_futuna': '🇼🇫', 'western_sahara': '🇪🇭', 'yemen': '🇾🇪',
    'zambia': '🇿🇲', 'zimbabwe': '🇿🇼', 'abacus': '🧮', 'adhesive_bandage':
    '🩹', 'admission_tickets': '🎟', 'adult': '🧑', 'adult_dark_skin_tone':
    '🧑🏿', 'adult_light_skin_tone': '🧑🏻', 'adult_medium-dark_skin_tone':
    '🧑🏾', 'adult_medium-light_skin_tone': '🧑🏼', 'adult_medium_skin_tone':
    '🧑🏽', 'aerial_tramway': '🚡', 'airplane': '✈', 'airplane_arrival': '🛬',
    'airplane_departure': '🛫', 'alarm_clock': '⏰', 'alembic': '⚗', 'alien':
    '👽', 'alien_monster': '👾', 'ambulance': '🚑', 'american_football': '🏈',
    'amphora': '🏺', 'anchor': '⚓', 'anger_symbol': '💢', 'angry_face': '😠',
    'angry_face_with_horns': '👿', 'anguished_face': '😧', 'ant': '🐜',
    'antenna_bars': '📶', 'anxious_face_with_sweat': '😰',
    'articulated_lorry': '🚛', 'artist_palette': '🎨', 'astonished_face': '😲',
    'atom_symbol': '⚛', 'auto_rickshaw': '🛺', 'automobile': '🚗', 'avocado':
    '🥑', 'axe': '🪓', 'baby': '👶', 'baby_angel': '👼',
    'baby_angel_dark_skin_tone': '👼🏿', 'baby_angel_light_skin_tone': '👼🏻',
    'baby_angel_medium-dark_skin_tone': '👼🏾',
    'baby_angel_medium-light_skin_tone': '👼🏼',
    'baby_angel_medium_skin_tone': '👼🏽', 'baby_bottle': '🍼', 'baby_chick':
    '🐤', 'baby_dark_skin_tone': '👶🏿', 'baby_light_skin_tone': '👶🏻',
    'baby_medium-dark_skin_tone': '👶🏾', 'baby_medium-light_skin_tone': '👶🏼',
    'baby_medium_skin_tone': '👶🏽', 'baby_symbol': '🚼',
    'backhand_index_pointing_down': '👇',
    'backhand_index_pointing_down_dark_skin_tone': '👇🏿',
    'backhand_index_pointing_down_light_skin_tone': '👇🏻',
    'backhand_index_pointing_down_medium-dark_skin_tone': '👇🏾',
    'backhand_index_pointing_down_medium-light_skin_tone': '👇🏼',
    'backhand_index_pointing_down_medium_skin_tone': '👇🏽',
    'backhand_index_pointing_left': '👈',
    'backhand_index_pointing_left_dark_skin_tone': '👈🏿',
    'backhand_index_pointing_left_light_skin_tone': '👈🏻',
    'backhand_index_pointing_left_medium-dark_skin_tone': '👈🏾',
    'backhand_index_pointing_left_medium-light_skin_tone': '👈🏼',
    'backhand_index_pointing_left_medium_skin_tone': '👈🏽',
    'backhand_index_pointing_right': '👉',
    'backhand_index_pointing_right_dark_skin_tone': '👉🏿',
    'backhand_index_pointing_right_light_skin_tone': '👉🏻',
    'backhand_index_pointing_right_medium-dark_skin_tone': '👉🏾',
    'backhand_index_pointing_right_medium-light_skin_tone': '👉🏼',
    'backhand_index_pointing_right_medium_skin_tone': '👉🏽',
    'backhand_index_pointing_up': '👆',
    'backhand_index_pointing_up_dark_skin_tone': '👆🏿',
    'backhand_index_pointing_up_light_skin_tone': '👆🏻',
    'backhand_index_pointing_up_medium-dark_skin_tone': '👆🏾',
    'backhand_index_pointing_up_medium-light_skin_tone': '👆🏼',
    'backhand_index_pointing_up_medium_skin_tone': '👆🏽', 'bacon': '🥓',
    'badger': '🦡', 'badminton': '🏸', 'bagel': '🥯', 'baggage_claim': '🛄',
    'baguette_bread': '🥖', 'balance_scale': '⚖', 'bald': '🦲', 'bald_man':
    '👨\u200d🦲', 'bald_woman': '👩\u200d🦲', 'ballet_shoes': '🩰', 'balloon':
    '🎈', 'ballot_box_with_ballot': '🗳', 'ballot_box_with_check': '☑',
    'banana': '🍌', 'banjo': '🪕', 'bank': '🏦', 'bar_chart': '📊',
    'barber_pole': '💈', 'baseball': '⚾', 'basket': '🧺', 'basketball': '🏀',
    'bat': '🦇', 'bathtub': '🛁', 'battery': '🔋', 'beach_with_umbrella': '🏖',
    'beaming_face_with_smiling_eyes': '😁', 'bear_face': '🐻',
    'bearded_person': '🧔', 'bearded_person_dark_skin_tone': '🧔🏿',
    'bearded_person_light_skin_tone': '🧔🏻',
    'bearded_person_medium-dark_skin_tone': '🧔🏾',
    'bearded_person_medium-light_skin_tone': '🧔🏼',
    'bearded_person_medium_skin_tone': '🧔🏽', 'beating_heart': '💓', 'bed':
    '🛏', 'beer_mug': '🍺', 'bell': '🔔', 'bell_with_slash': '🔕',
    'bellhop_bell': '🛎', 'bento_box': '🍱', 'beverage_box': '🧃', 'bicycle':
    '🚲', 'bikini': '👙', 'billed_cap': '🧢', 'biohazard': '☣', 'bird': '🐦',
    'birthday_cake': '🎂', 'black_circle': '⚫', 'black_flag': '🏴',
    'black_heart': '🖤', 'black_large_square': '⬛',
    'black_medium-small_square': '◾', 'black_medium_square': '◼',
    'black_nib': '✒', 'black_small_square': '▪', 'black_square_button': '🔲',
    'blond-haired_man': '👱\u200d♂️', 'blond-haired_man_dark_skin_tone':
    '👱🏿\u200d♂️', 'blond-haired_man_light_skin_tone': '👱🏻\u200d♂️',
    'blond-haired_man_medium-dark_skin_tone': '👱🏾\u200d♂️',
    'blond-haired_man_medium-light_skin_tone': '👱🏼\u200d♂️',
    'blond-haired_man_medium_skin_tone': '👱🏽\u200d♂️',
    'blond-haired_person': '👱', 'blond-haired_person_dark_skin_tone': '👱🏿',
    'blond-haired_person_light_skin_tone': '👱🏻',
    'blond-haired_person_medium-dark_skin_tone': '👱🏾',
    'blond-haired_person_medium-light_skin_tone': '👱🏼',
    'blond-haired_person_medium_skin_tone': '👱🏽', 'blond-haired_woman':
    '👱\u200d♀️', 'blond-haired_woman_dark_skin_tone': '👱🏿\u200d♀️',
    'blond-haired_woman_light_skin_tone': '👱🏻\u200d♀️',
    'blond-haired_woman_medium-dark_skin_tone': '👱🏾\u200d♀️',
    'blond-haired_woman_medium-light_skin_tone': '👱🏼\u200d♀️',
    'blond-haired_woman_medium_skin_tone': '👱🏽\u200d♀️', 'blossom': '🌼',
    'blowfish': '🐡', 'blue_book': '📘', 'blue_circle': '🔵', 'blue_heart':
    '💙', 'blue_square': '🟦', 'boar': '🐗', 'bomb': '💣', 'bone': '🦴',
    'bookmark': '🔖', 'bookmark_tabs': '📑', 'books': '📚',
    'bottle_with_popping_cork': '🍾', 'bouquet': '💐', 'bow_and_arrow': '🏹',
    'bowl_with_spoon': '🥣', 'bowling': '🎳', 'boxing_glove': '🥊', 'boy': '👦',
    'boy_dark_skin_tone': '👦🏿', 'boy_light_skin_tone': '👦🏻',
    'boy_medium-dark_skin_tone': '👦🏾', 'boy_medium-light_skin_tone': '👦🏼',
    'boy_medium_skin_tone': '👦🏽', 'brain': '🧠', 'bread': '🍞',
    'breast-feeding': '🤱', 'breast-feeding_dark_skin_tone': '🤱🏿',
    'breast-feeding_light_skin_tone': '🤱🏻',
    'breast-feeding_medium-dark_skin_tone': '🤱🏾',
    'breast-feeding_medium-light_skin_tone': '🤱🏼',
    'breast-feeding_medium_skin_tone': '🤱🏽', 'brick': '🧱',
    'bride_with_veil': '👰', 'bride_with_veil_dark_skin_tone': '👰🏿',
    'bride_with_veil_light_skin_tone': '👰🏻',
    'bride_with_veil_medium-dark_skin_tone': '👰🏾',
    'bride_with_veil_medium-light_skin_tone': '👰🏼',
    'bride_with_veil_medium_skin_tone': '👰🏽', 'bridge_at_night': '🌉',
    'briefcase': '💼', 'briefs': '🩲', 'bright_button': '🔆', 'broccoli': '🥦',
    'broken_heart': '💔', 'broom': '🧹', 'brown_circle': '🟤', 'brown_heart':
    '🤎', 'brown_square': '🟫', 'bug': '🐛', 'building_construction': '🏗',
    'bullet_train': '🚅', 'burrito': '🌯', 'bus': '🚌', 'bus_stop': '🚏',
    'bust_in_silhouette': '👤', 'busts_in_silhouette': '👥', 'butter': '🧈',
    'butterfly': '🦋', 'cactus': '🌵', 'calendar': '📆', 'call_me_hand': '🤙',
    'call_me_hand_dark_skin_tone': '🤙🏿', 'call_me_hand_light_skin_tone':
    '🤙🏻', 'call_me_hand_medium-dark_skin_tone': '🤙🏾',
    'call_me_hand_medium-light_skin_tone': '🤙🏼',
    'call_me_hand_medium_skin_tone': '🤙🏽', 'camel': '🐫', 'camera': '📷',
    'camera_with_flash': '📸', 'camping': '🏕', 'candle': '🕯', 'candy': '🍬',
    'canned_food': '🥫', 'canoe': '🛶', 'card_file_box': '🗃', 'card_index':
    '📇', 'card_index_dividers': '🗂', 'carousel_horse': '🎠', 'carp_streamer':
    '🎏', 'carrot': '🥕', 'castle': '🏰', 'cat': '🐱', 'cat_face': '🐱',
    'cat_face_with_tears_of_joy': '😹', 'cat_face_with_wry_smile': '😼',
    'chains': '⛓', 'chair': '🪑', 'chart_decreasing': '📉',
    'chart_increasing': '📈', 'chart_increasing_with_yen': '💹',
    'cheese_wedge': '🧀', 'chequered_flag': '🏁', 'cherries': '🍒',
    'cherry_blossom': '🌸', 'chess_pawn': '♟', 'chestnut': '🌰', 'chicken':
    '🐔', 'child': '🧒', 'child_dark_skin_tone': '🧒🏿',
    'child_light_skin_tone': '🧒🏻', 'child_medium-dark_skin_tone': '🧒🏾',
    'child_medium-light_skin_tone': '🧒🏼', 'child_medium_skin_tone': '🧒🏽',
    'children_crossing': '🚸', 'chipmunk': '🐿', 'chocolate_bar': '🍫',
    'chopsticks': '🥢', 'church': '⛪', 'cigarette': '🚬', 'cinema': '🎦',
    'circled_m': 'Ⓜ', 'circus_tent': '🎪', 'cityscape': '🏙',
    'cityscape_at_dusk': '🌆', 'clamp': '🗜', 'clapper_board': '🎬',
    'clapping_hands': '👏', 'clapping_hands_dark_skin_tone': '👏🏿',
    'clapping_hands_light_skin_tone': '👏🏻',
    'clapping_hands_medium-dark_skin_tone': '👏🏾',
    'clapping_hands_medium-light_skin_tone': '👏🏼',
    'clapping_hands_medium_skin_tone': '👏🏽', 'classical_building': '🏛',
    'clinking_beer_mugs': '🍻', 'clinking_glasses': '🥂', 'clipboard': '📋',
    'clockwise_vertical_arrows': '🔃', 'closed_book': '📕',
    'closed_mailbox_with_lowered_flag': '📪',
    'closed_mailbox_with_raised_flag': '📫', 'closed_umbrella': '🌂', 'cloud':
    '☁', 'cloud_with_lightning': '🌩', 'cloud_with_lightning_and_rain': '⛈',
    'cloud_with_rain': '🌧', 'cloud_with_snow': '🌨', 'clown_face': '🤡',
    'club_suit': '♣', 'clutch_bag': '👝', 'coat': '🧥', 'cocktail_glass': '🍸',
    'coconut': '🥥', 'coffin': '⚰', 'cold_face': '🥶', 'collision': '💥',
    'comet': '☄', 'compass': '🧭', 'computer_disk': '💽', 'computer_mouse':
    '🖱', 'confetti_ball': '🎊', 'confounded_face': '😖', 'confused_face': '😕',
    'construction': '🚧', 'construction_worker': '👷',
    'construction_worker_dark_skin_tone': '👷🏿',
    'construction_worker_light_skin_tone': '👷🏻',
    'construction_worker_medium-dark_skin_tone': '👷🏾',
    'construction_worker_medium-light_skin_tone': '👷🏼',
    'construction_worker_medium_skin_tone': '👷🏽', 'control_knobs': '🎛',
    'convenience_store': '🏪', 'cooked_rice': '🍚', 'cookie': '🍪', 'cooking':
    '🍳', 'copyright': '©', 'couch_and_lamp': '🛋',
    'counterclockwise_arrows_button': '🔄', 'couple_with_heart': '💑',
    'couple_with_heart_man_man': '👨\u200d❤️\u200d👨',
    'couple_with_heart_woman_man': '👩\u200d❤️\u200d👨',
    'couple_with_heart_woman_woman': '👩\u200d❤️\u200d👩', 'cow': '🐮',
    'cow_face': '🐮', 'cowboy_hat_face': '🤠', 'crab': '🦀', 'crayon': '🖍',
    'credit_card': '💳', 'crescent_moon': '🌙', 'cricket': '🦗',
    'cricket_game': '🏏', 'crocodile': '🐊', 'croissant': '🥐', 'cross_mark':
    '❌', 'cross_mark_button': '❎', 'crossed_fingers': '🤞',
    'crossed_fingers_dark_skin_tone': '🤞🏿',
    'crossed_fingers_light_skin_tone': '🤞🏻',
    'crossed_fingers_medium-dark_skin_tone': '🤞🏾',
    'crossed_fingers_medium-light_skin_tone': '🤞🏼',
    'crossed_fingers_medium_skin_tone': '🤞🏽', 'crossed_flags': '🎌',
    'crossed_swords': '⚔', 'crown': '👑', 'crying_cat_face': '😿',
    'crying_face': '😢', 'crystal_ball': '🔮', 'cucumber': '🥒', 'cupcake':
    '🧁', 'cup_with_straw': '🥤', 'curling_stone': '🥌', 'curly_hair': '🦱',
    'curly-haired_man': '👨\u200d🦱', 'curly-haired_woman': '👩\u200d🦱',
    'curly_loop': '➰', 'currency_exchange': '💱', 'curry_rice': '🍛',
    'custard': '🍮', 'customs': '🛃', 'cut_of_meat': '🥩', 'cyclone': '🌀',
    'dagger': '🗡', 'dango': '🍡', 'dashing_away': '💨', 'deaf_person': '🧏',
    'deciduous_tree': '🌳', 'deer': '🦌', 'delivery_truck': '🚚',
    'department_store': '🏬', 'derelict_house': '🏚', 'desert': '🏜',
    'desert_island': '🏝', 'desktop_computer': '🖥', 'detective': '🕵',
    'detective_dark_skin_tone': '🕵🏿', 'detective_light_skin_tone': '🕵🏻',
    'detective_medium-dark_skin_tone': '🕵🏾',
    'detective_medium-light_skin_tone': '🕵🏼', 'detective_medium_skin_tone':
    '🕵🏽', 'diamond_suit': '♦', 'diamond_with_a_dot': '💠', 'dim_button': '🔅',
    'direct_hit': '🎯', 'disappointed_face': '😞', 'diving_mask': '🤿',
    'diya_lamp': '🪔', 'dizzy': '💫', 'dizzy_face': '😵', 'dna': '🧬', 'dog':
    '🐶', 'dog_face': '🐶', 'dollar_banknote': '💵', 'dolphin': '🐬', 'door':
    '🚪', 'dotted_six-pointed_star': '🔯', 'double_curly_loop': '➿',
    'double_exclamation_mark': '‼', 'doughnut': '🍩', 'dove': '🕊',
    'down-left_arrow': '↙', 'down-right_arrow': '↘', 'down_arrow': '⬇',
    'downcast_face_with_sweat': '😓', 'downwards_button': '🔽', 'dragon': '🐉',
    'dragon_face': '🐲', 'dress': '👗', 'drooling_face': '🤤', 'drop_of_blood':
    '🩸', 'droplet': '💧', 'drum': '🥁', 'duck': '🦆', 'dumpling': '🥟', 'dvd':
    '📀', 'e-mail': '📧', 'eagle': '🦅', 'ear': '👂', 'ear_dark_skin_tone':
    '👂🏿', 'ear_light_skin_tone': '👂🏻', 'ear_medium-dark_skin_tone': '👂🏾',
    'ear_medium-light_skin_tone': '👂🏼', 'ear_medium_skin_tone': '👂🏽',
    'ear_of_corn': '🌽', 'ear_with_hearing_aid': '🦻', 'egg': '🍳', 'eggplant':
    '🍆', 'eight-pointed_star': '✴', 'eight-spoked_asterisk': '✳',
    'eight-thirty': '🕣', 'eight_o’clock': '🕗', 'eject_button': '⏏',
    'electric_plug': '🔌', 'elephant': '🐘', 'eleven-thirty': '🕦',
    'eleven_o’clock': '🕚', 'elf': '🧝', 'elf_dark_skin_tone': '🧝🏿',
    'elf_light_skin_tone': '🧝🏻', 'elf_medium-dark_skin_tone': '🧝🏾',
    'elf_medium-light_skin_tone': '🧝🏼', 'elf_medium_skin_tone': '🧝🏽',
    'envelope': '✉', 'envelope_with_arrow': '📩', 'euro_banknote': '💶',
    'evergreen_tree': '🌲', 'ewe': '🐑', 'exclamation_mark': '❗',
    'exclamation_question_mark': '⁉', 'exploding_head': '🤯',
    'expressionless_face': '😑', 'eye': '👁', 'eye_in_speech_bubble':
    '👁️\u200d🗨️', 'eyes': '👀', 'face_blowing_a_kiss': '😘',
    'face_savoring_food': '😋', 'face_screaming_in_fear': '😱',
    'face_vomiting': '🤮', 'face_with_hand_over_mouth': '🤭',
    'face_with_head-bandage': '🤕', 'face_with_medical_mask': '😷',
    'face_with_monocle': '🧐', 'face_with_open_mouth': '😮',
    'face_with_raised_eyebrow': '🤨', 'face_with_rolling_eyes': '🙄',
    'face_with_steam_from_nose': '😤', 'face_with_symbols_on_mouth': '🤬',
    'face_with_tears_of_joy': '😂', 'face_with_thermometer': '🤒',
    'face_with_tongue': '😛', 'face_without_mouth': '😶', 'factory': '🏭',
    'fairy': '🧚', 'fairy_dark_skin_tone': '🧚🏿', 'fairy_light_skin_tone':
    '🧚🏻', 'fairy_medium-dark_skin_tone': '🧚🏾',
    'fairy_medium-light_skin_tone': '🧚🏼', 'fairy_medium_skin_tone': '🧚🏽',
    'falafel': '🧆', 'fallen_leaf': '🍂', 'family': '👪', 'family_man_boy':
    '👨\u200d👦', 'family_man_boy_boy': '👨\u200d👦\u200d👦', 'family_man_girl':
    '👨\u200d👧', 'family_man_girl_boy': '👨\u200d👧\u200d👦',
    'family_man_girl_girl': '👨\u200d👧\u200d👧', 'family_man_man_boy':
    '👨\u200d👨\u200d👦', 'family_man_man_boy_boy': '👨\u200d👨\u200d👦\u200d👦',
    'family_man_man_girl': '👨\u200d👨\u200d👧', 'family_man_man_girl_boy':
    '👨\u200d👨\u200d👧\u200d👦', 'family_man_man_girl_girl':
    '👨\u200d👨\u200d👧\u200d👧', 'family_man_woman_boy': '👨\u200d👩\u200d👦',
    'family_man_woman_boy_boy': '👨\u200d👩\u200d👦\u200d👦',
    'family_man_woman_girl': '👨\u200d👩\u200d👧', 'family_man_woman_girl_boy':
    '👨\u200d👩\u200d👧\u200d👦', 'family_man_woman_girl_girl':
    '👨\u200d👩\u200d👧\u200d👧', 'family_woman_boy': '👩\u200d👦',
    'family_woman_boy_boy': '👩\u200d👦\u200d👦', 'family_woman_girl':
    '👩\u200d👧', 'family_woman_girl_boy': '👩\u200d👧\u200d👦',
    'family_woman_girl_girl': '👩\u200d👧\u200d👧', 'family_woman_woman_boy':
    '👩\u200d👩\u200d👦', 'family_woman_woman_boy_boy':
    '👩\u200d👩\u200d👦\u200d👦', 'family_woman_woman_girl': '👩\u200d👩\u200d👧',
    'family_woman_woman_girl_boy': '👩\u200d👩\u200d👧\u200d👦',
    'family_woman_woman_girl_girl': '👩\u200d👩\u200d👧\u200d👧',
    'fast-forward_button': '⏩', 'fast_down_button': '⏬',
    'fast_reverse_button': '⏪', 'fast_up_button': '⏫', 'fax_machine': '📠',
    'fearful_face': '😨', 'female_sign': '♀', 'ferris_wheel': '🎡', 'ferry':
    '⛴', 'field_hockey': '🏑', 'file_cabinet': '🗄', 'file_folder': '📁',
    'film_frames': '🎞', 'film_projector': '📽', 'fire': '🔥',
    'fire_extinguisher': '🧯', 'firecracker': '🧨', 'fire_engine': '🚒',
    'fireworks': '🎆', 'first_quarter_moon': '🌓', 'first_quarter_moon_face':
    '🌛', 'fish': '🐟', 'fish_cake_with_swirl': '🍥', 'fishing_pole': '🎣',
    'five-thirty': '🕠', 'five_o’clock': '🕔', 'flag_in_hole': '⛳',
    'flamingo': '🦩', 'flashlight': '🔦', 'flat_shoe': '🥿', 'fleur-de-lis':
    '⚜', 'flexed_biceps': '💪', 'flexed_biceps_dark_skin_tone': '💪🏿',
    'flexed_biceps_light_skin_tone': '💪🏻',
    'flexed_biceps_medium-dark_skin_tone': '💪🏾',
    'flexed_biceps_medium-light_skin_tone': '💪🏼',
    'flexed_biceps_medium_skin_tone': '💪🏽', 'floppy_disk': '💾',
    'flower_playing_cards': '🎴', 'flushed_face': '😳', 'flying_disc': '🥏',
    'flying_saucer': '🛸', 'fog': '🌫', 'foggy': '🌁', 'folded_hands': '🙏',
    'folded_hands_dark_skin_tone': '🙏🏿', 'folded_hands_light_skin_tone':
    '🙏🏻', 'folded_hands_medium-dark_skin_tone': '🙏🏾',
    'folded_hands_medium-light_skin_tone': '🙏🏼',
    'folded_hands_medium_skin_tone': '🙏🏽', 'foot': '🦶', 'footprints': '👣',
    'fork_and_knife': '🍴', 'fork_and_knife_with_plate': '🍽',
    'fortune_cookie': '🥠', 'fountain': '⛲', 'fountain_pen': '🖋',
    'four-thirty': '🕟', 'four_leaf_clover': '🍀', 'four_o’clock': '🕓',
    'fox_face': '🦊', 'framed_picture': '🖼', 'french_fries': '🍟',
    'fried_shrimp': '🍤', 'frog_face': '🐸', 'front-facing_baby_chick': '🐥',
    'frowning_face': '☹', 'frowning_face_with_open_mouth': '😦', 'fuel_pump':
    '⛽', 'full_moon': '🌕', 'full_moon_face': '🌝', 'funeral_urn': '⚱',
    'game_die': '🎲', 'garlic': '🧄', 'gear': '⚙', 'gem_stone': '💎', 'genie':
    '🧞', 'ghost': '👻', 'giraffe': '🦒', 'girl': '👧', 'girl_dark_skin_tone':
    '👧🏿', 'girl_light_skin_tone': '👧🏻', 'girl_medium-dark_skin_tone': '👧🏾',
    'girl_medium-light_skin_tone': '👧🏼', 'girl_medium_skin_tone': '👧🏽',
    'glass_of_milk': '🥛', 'glasses': '👓', 'globe_showing_americas': '🌎',
    'globe_showing_asia-australia': '🌏', 'globe_showing_europe-africa': '🌍',
    'globe_with_meridians': '🌐', 'gloves': '🧤', 'glowing_star': '🌟',
    'goal_net': '🥅', 'goat': '🐐', 'goblin': '👺', 'goggles': '🥽', 'gorilla':
    '🦍', 'graduation_cap': '🎓', 'grapes': '🍇', 'green_apple': '🍏',
    'green_book': '📗', 'green_circle': '🟢', 'green_heart': '💚',
    'green_salad': '🥗', 'green_square': '🟩', 'grimacing_face': '😬',
    'grinning_cat_face': '😺', 'grinning_cat_face_with_smiling_eyes': '😸',
    'grinning_face': '😀', 'grinning_face_with_big_eyes': '😃',
    'grinning_face_with_smiling_eyes': '😄', 'grinning_face_with_sweat': '😅',
    'grinning_squinting_face': '😆', 'growing_heart': '💗', 'guard': '💂',
    'guard_dark_skin_tone': '💂🏿', 'guard_light_skin_tone': '💂🏻',
    'guard_medium-dark_skin_tone': '💂🏾', 'guard_medium-light_skin_tone':
    '💂🏼', 'guard_medium_skin_tone': '💂🏽', 'guide_dog': '🦮', 'guitar': '🎸',
    'hamburger': '🍔', 'hammer': '🔨', 'hammer_and_pick': '⚒',
    'hammer_and_wrench': '🛠', 'hamster_face': '🐹',
    'hand_with_fingers_splayed': '🖐',
    'hand_with_fingers_splayed_dark_skin_tone': '🖐🏿',
    'hand_with_fingers_splayed_light_skin_tone': '🖐🏻',
    'hand_with_fingers_splayed_medium-dark_skin_tone': '🖐🏾',
    'hand_with_fingers_splayed_medium-light_skin_tone': '🖐🏼',
    'hand_with_fingers_splayed_medium_skin_tone': '🖐🏽', 'handbag': '👜',
    'handshake': '🤝', 'hatching_chick': '🐣', 'headphone': '🎧',
    'hear-no-evil_monkey': '🙉', 'heart_decoration': '💟', 'heart_suit': '♥',
    'heart_with_arrow': '💘', 'heart_with_ribbon': '💝', 'heavy_check_mark':
    '✔', 'heavy_division_sign': '➗', 'heavy_dollar_sign': '💲',
    'heavy_heart_exclamation': '❣', 'heavy_large_circle': '⭕',
    'heavy_minus_sign': '➖', 'heavy_multiplication_x': '✖',
    'heavy_plus_sign': '➕', 'hedgehog': '🦔', 'helicopter': '🚁', 'herb': '🌿',
    'hibiscus': '🌺', 'high-heeled_shoe': '👠', 'high-speed_train': '🚄',
    'high_voltage': '⚡', 'hiking_boot': '🥾', 'hindu_temple': '🛕',
    'hippopotamus': '🦛', 'hole': '🕳', 'honey_pot': '🍯', 'honeybee': '🐝',
    'horizontal_traffic_light': '🚥', 'horse': '🐴', 'horse_face': '🐴',
    'horse_racing': '🏇', 'horse_racing_dark_skin_tone': '🏇🏿',
    'horse_racing_light_skin_tone': '🏇🏻',
    'horse_racing_medium-dark_skin_tone': '🏇🏾',
    'horse_racing_medium-light_skin_tone': '🏇🏼',
    'horse_racing_medium_skin_tone': '🏇🏽', 'hospital': '🏥', 'hot_beverage':
    '☕', 'hot_dog': '🌭', 'hot_face': '🥵', 'hot_pepper': '🌶', 'hot_springs':
    '♨', 'hotel': '🏨', 'hourglass_done': '⌛', 'hourglass_not_done': '⏳',
    'house': '🏠', 'house_with_garden': '🏡', 'houses': '🏘', 'hugging_face':
    '🤗', 'hundred_points': '💯', 'hushed_face': '😯', 'ice': '🧊', 'ice_cream':
    '🍨', 'ice_hockey': '🏒', 'ice_skate': '⛸', 'inbox_tray': '📥',
    'incoming_envelope': '📨', 'index_pointing_up': '☝',
    'index_pointing_up_dark_skin_tone': '☝🏿',
    'index_pointing_up_light_skin_tone': '☝🏻',
    'index_pointing_up_medium-dark_skin_tone': '☝🏾',
    'index_pointing_up_medium-light_skin_tone': '☝🏼',
    'index_pointing_up_medium_skin_tone': '☝🏽', 'infinity': '♾',
    'information': 'ℹ', 'input_latin_letters': '🔤', 'input_latin_lowercase':
    '🔡', 'input_latin_uppercase': '🔠', 'input_numbers': '🔢',
    'input_symbols': '🔣', 'jack-o-lantern': '🎃', 'jeans': '👖', 'jigsaw':
    '🧩', 'joker': '🃏', 'joystick': '🕹', 'kaaba': '🕋', 'kangaroo': '🦘',
    'key': '🔑', 'keyboard': '⌨', 'keycap_#': '#️⃣', 'keycap_*': '*️⃣',
    'keycap_0': '0️⃣', 'keycap_1': '1️⃣', 'keycap_10': '🔟', 'keycap_2':
    '2️⃣', 'keycap_3': '3️⃣', 'keycap_4': '4️⃣', 'keycap_5': '5️⃣',
    'keycap_6': '6️⃣', 'keycap_7': '7️⃣', 'keycap_8': '8️⃣', 'keycap_9':
    '9️⃣', 'kick_scooter': '🛴', 'kimono': '👘', 'kiss': '💋', 'kiss_man_man':
    '👨\u200d❤️\u200d💋\u200d👨', 'kiss_mark': '💋', 'kiss_woman_man':
    '👩\u200d❤️\u200d💋\u200d👨', 'kiss_woman_woman':
    '👩\u200d❤️\u200d💋\u200d👩', 'kissing_cat_face': '😽', 'kissing_face': '😗',
    'kissing_face_with_closed_eyes': '😚', 'kissing_face_with_smiling_eyes':
    '😙', 'kitchen_knife': '🔪', 'kite': '🪁', 'kiwi_fruit': '🥝', 'koala': '🐨',
    'lab_coat': '🥼', 'label': '🏷', 'lacrosse': '🥍', 'lady_beetle': '🐞',
    'laptop_computer': '💻', 'large_blue_diamond': '🔷',
    'large_orange_diamond': '🔶', 'last_quarter_moon': '🌗',
    'last_quarter_moon_face': '🌜', 'last_track_button': '⏮', 'latin_cross':
    '✝', 'leaf_fluttering_in_wind': '🍃', 'leafy_green': '🥬', 'ledger': '📒',
    'left-facing_fist': '🤛', 'left-facing_fist_dark_skin_tone': '🤛🏿',
    'left-facing_fist_light_skin_tone': '🤛🏻',
    'left-facing_fist_medium-dark_skin_tone': '🤛🏾',
    'left-facing_fist_medium-light_skin_tone': '🤛🏼',
    'left-facing_fist_medium_skin_tone': '🤛🏽', 'left-right_arrow': '↔',
    'left_arrow': '⬅', 'left_arrow_curving_right': '↪', 'left_luggage': '🛅',
    'left_speech_bubble': '🗨', 'leg': '🦵', 'lemon': '🍋', 'leopard': '🐆',
    'level_slider': '🎚', 'light_bulb': '💡', 'light_rail': '🚈', 'link': '🔗',
    'linked_paperclips': '🖇', 'lion_face': '🦁', 'lipstick': '💄',
    'litter_in_bin_sign': '🚮', 'lizard': '🦎', 'llama': '🦙', 'lobster': '🦞',
    'locked': '🔒', 'locked_with_key': '🔐', 'locked_with_pen': '🔏',
    'locomotive': '🚂', 'lollipop': '🍭', 'lotion_bottle': '🧴',
    'loudly_crying_face': '😭', 'loudspeaker': '📢', 'love-you_gesture': '🤟',
    'love-you_gesture_dark_skin_tone': '🤟🏿',
    'love-you_gesture_light_skin_tone': '🤟🏻',
    'love-you_gesture_medium-dark_skin_tone': '🤟🏾',
    'love-you_gesture_medium-light_skin_tone': '🤟🏼',
    'love-you_gesture_medium_skin_tone': '🤟🏽', 'love_hotel': '🏩',
    'love_letter': '💌', 'luggage': '🧳', 'lying_face': '🤥', 'mage': '🧙',
    'mage_dark_skin_tone': '🧙🏿', 'mage_light_skin_tone': '🧙🏻',
    'mage_medium-dark_skin_tone': '🧙🏾', 'mage_medium-light_skin_tone': '🧙🏼',
    'mage_medium_skin_tone': '🧙🏽', 'magnet': '🧲',
    'magnifying_glass_tilted_left': '🔍', 'magnifying_glass_tilted_right':
    '🔎', 'mahjong_red_dragon': '🀄', 'male_sign': '♂', 'man': '👨',
    'man_and_woman_holding_hands': '👫', 'man_artist': '👨\u200d🎨',
    'man_artist_dark_skin_tone': '👨🏿\u200d🎨', 'man_artist_light_skin_tone':
    '👨🏻\u200d🎨', 'man_artist_medium-dark_skin_tone': '👨🏾\u200d🎨',
    'man_artist_medium-light_skin_tone': '👨🏼\u200d🎨',
    'man_artist_medium_skin_tone': '👨🏽\u200d🎨', 'man_astronaut': '👨\u200d🚀',
    'man_astronaut_dark_skin_tone': '👨🏿\u200d🚀',
    'man_astronaut_light_skin_tone': '👨🏻\u200d🚀',
    'man_astronaut_medium-dark_skin_tone': '👨🏾\u200d🚀',
    'man_astronaut_medium-light_skin_tone': '👨🏼\u200d🚀',
    'man_astronaut_medium_skin_tone': '👨🏽\u200d🚀', 'man_biking':
    '🚴\u200d♂️', 'man_biking_dark_skin_tone': '🚴🏿\u200d♂️',
    'man_biking_light_skin_tone': '🚴🏻\u200d♂️',
    'man_biking_medium-dark_skin_tone': '🚴🏾\u200d♂️',
    'man_biking_medium-light_skin_tone': '🚴🏼\u200d♂️',
    'man_biking_medium_skin_tone': '🚴🏽\u200d♂️', 'man_bouncing_ball':
    '⛹️\u200d♂️', 'man_bouncing_ball_dark_skin_tone': '⛹🏿\u200d♂️',
    'man_bouncing_ball_light_skin_tone': '⛹🏻\u200d♂️',
    'man_bouncing_ball_medium-dark_skin_tone': '⛹🏾\u200d♂️',
    'man_bouncing_ball_medium-light_skin_tone': '⛹🏼\u200d♂️',
    'man_bouncing_ball_medium_skin_tone': '⛹🏽\u200d♂️', 'man_bowing':
    '🙇\u200d♂️', 'man_bowing_dark_skin_tone': '🙇🏿\u200d♂️',
    'man_bowing_light_skin_tone': '🙇🏻\u200d♂️',
    'man_bowing_medium-dark_skin_tone': '🙇🏾\u200d♂️',
    'man_bowing_medium-light_skin_tone': '🙇🏼\u200d♂️',
    'man_bowing_medium_skin_tone': '🙇🏽\u200d♂️', 'man_cartwheeling':
    '🤸\u200d♂️', 'man_cartwheeling_dark_skin_tone': '🤸🏿\u200d♂️',
    'man_cartwheeling_light_skin_tone': '🤸🏻\u200d♂️',
    'man_cartwheeling_medium-dark_skin_tone': '🤸🏾\u200d♂️',
    'man_cartwheeling_medium-light_skin_tone': '🤸🏼\u200d♂️',
    'man_cartwheeling_medium_skin_tone': '🤸🏽\u200d♂️', 'man_climbing':
    '🧗\u200d♂️', 'man_climbing_dark_skin_tone': '🧗🏿\u200d♂️',
    'man_climbing_light_skin_tone': '🧗🏻\u200d♂️',
    'man_climbing_medium-dark_skin_tone': '🧗🏾\u200d♂️',
    'man_climbing_medium-light_skin_tone': '🧗🏼\u200d♂️',
    'man_climbing_medium_skin_tone': '🧗🏽\u200d♂️',
    'man_construction_worker': '👷\u200d♂️',
    'man_construction_worker_dark_skin_tone': '👷🏿\u200d♂️',
    'man_construction_worker_light_skin_tone': '👷🏻\u200d♂️',
    'man_construction_worker_medium-dark_skin_tone': '👷🏾\u200d♂️',
    'man_construction_worker_medium-light_skin_tone': '👷🏼\u200d♂️',
    'man_construction_worker_medium_skin_tone': '👷🏽\u200d♂️', 'man_cook':
    '👨\u200d🍳', 'man_cook_dark_skin_tone': '👨🏿\u200d🍳',
    'man_cook_light_skin_tone': '👨🏻\u200d🍳',
    'man_cook_medium-dark_skin_tone': '👨🏾\u200d🍳',
    'man_cook_medium-light_skin_tone': '👨🏼\u200d🍳',
    'man_cook_medium_skin_tone': '👨🏽\u200d🍳', 'man_dancing': '🕺',
    'man_dancing_dark_skin_tone': '🕺🏿', 'man_dancing_light_skin_tone': '🕺🏻',
    'man_dancing_medium-dark_skin_tone': '🕺🏾',
    'man_dancing_medium-light_skin_tone': '🕺🏼',
    'man_dancing_medium_skin_tone': '🕺🏽', 'man_dark_skin_tone': '👨🏿',
    'man_detective': '🕵️\u200d♂️', 'man_detective_dark_skin_tone':
    '🕵🏿\u200d♂️', 'man_detective_light_skin_tone': '🕵🏻\u200d♂️',
    'man_detective_medium-dark_skin_tone': '🕵🏾\u200d♂️',
    'man_detective_medium-light_skin_tone': '🕵🏼\u200d♂️',
    'man_detective_medium_skin_tone': '🕵🏽\u200d♂️', 'man_elf': '🧝\u200d♂️',
    'man_elf_dark_skin_tone': '🧝🏿\u200d♂️', 'man_elf_light_skin_tone':
    '🧝🏻\u200d♂️', 'man_elf_medium-dark_skin_tone': '🧝🏾\u200d♂️',
    'man_elf_medium-light_skin_tone': '🧝🏼\u200d♂️',
    'man_elf_medium_skin_tone': '🧝🏽\u200d♂️', 'man_facepalming':
    '🤦\u200d♂️', 'man_facepalming_dark_skin_tone': '🤦🏿\u200d♂️',
    'man_facepalming_light_skin_tone': '🤦🏻\u200d♂️',
    'man_facepalming_medium-dark_skin_tone': '🤦🏾\u200d♂️',
    'man_facepalming_medium-light_skin_tone': '🤦🏼\u200d♂️',
    'man_facepalming_medium_skin_tone': '🤦🏽\u200d♂️', 'man_factory_worker':
    '👨\u200d🏭', 'man_factory_worker_dark_skin_tone': '👨🏿\u200d🏭',
    'man_factory_worker_light_skin_tone': '👨🏻\u200d🏭',
    'man_factory_worker_medium-dark_skin_tone': '👨🏾\u200d🏭',
    'man_factory_worker_medium-light_skin_tone': '👨🏼\u200d🏭',
    'man_factory_worker_medium_skin_tone': '👨🏽\u200d🏭', 'man_fairy':
    '🧚\u200d♂️', 'man_fairy_dark_skin_tone': '🧚🏿\u200d♂️',
    'man_fairy_light_skin_tone': '🧚🏻\u200d♂️',
    'man_fairy_medium-dark_skin_tone': '🧚🏾\u200d♂️',
    'man_fairy_medium-light_skin_tone': '🧚🏼\u200d♂️',
    'man_fairy_medium_skin_tone': '🧚🏽\u200d♂️', 'man_farmer': '👨\u200d🌾',
    'man_farmer_dark_skin_tone': '👨🏿\u200d🌾', 'man_farmer_light_skin_tone':
    '👨🏻\u200d🌾', 'man_farmer_medium-dark_skin_tone': '👨🏾\u200d🌾',
    'man_farmer_medium-light_skin_tone': '👨🏼\u200d🌾',
    'man_farmer_medium_skin_tone': '👨🏽\u200d🌾', 'man_firefighter':
    '👨\u200d🚒', 'man_firefighter_dark_skin_tone': '👨🏿\u200d🚒',
    'man_firefighter_light_skin_tone': '👨🏻\u200d🚒',
    'man_firefighter_medium-dark_skin_tone': '👨🏾\u200d🚒',
    'man_firefighter_medium-light_skin_tone': '👨🏼\u200d🚒',
    'man_firefighter_medium_skin_tone': '👨🏽\u200d🚒', 'man_frowning':
    '🙍\u200d♂️', 'man_frowning_dark_skin_tone': '🙍🏿\u200d♂️',
    'man_frowning_light_skin_tone': '🙍🏻\u200d♂️',
    'man_frowning_medium-dark_skin_tone': '🙍🏾\u200d♂️',
    'man_frowning_medium-light_skin_tone': '🙍🏼\u200d♂️',
    'man_frowning_medium_skin_tone': '🙍🏽\u200d♂️', 'man_genie': '🧞\u200d♂️',
    'man_gesturing_no': '🙅\u200d♂️', 'man_gesturing_no_dark_skin_tone':
    '🙅🏿\u200d♂️', 'man_gesturing_no_light_skin_tone': '🙅🏻\u200d♂️',
    'man_gesturing_no_medium-dark_skin_tone': '🙅🏾\u200d♂️',
    'man_gesturing_no_medium-light_skin_tone': '🙅🏼\u200d♂️',
    'man_gesturing_no_medium_skin_tone': '🙅🏽\u200d♂️', 'man_gesturing_ok':
    '🙆\u200d♂️', 'man_gesturing_ok_dark_skin_tone': '🙆🏿\u200d♂️',
    'man_gesturing_ok_light_skin_tone': '🙆🏻\u200d♂️',
    'man_gesturing_ok_medium-dark_skin_tone': '🙆🏾\u200d♂️',
    'man_gesturing_ok_medium-light_skin_tone': '🙆🏼\u200d♂️',
    'man_gesturing_ok_medium_skin_tone': '🙆🏽\u200d♂️',
    'man_getting_haircut': '💇\u200d♂️',
    'man_getting_haircut_dark_skin_tone': '💇🏿\u200d♂️',
    'man_getting_haircut_light_skin_tone': '💇🏻\u200d♂️',
    'man_getting_haircut_medium-dark_skin_tone': '💇🏾\u200d♂️',
    'man_getting_haircut_medium-light_skin_tone': '💇🏼\u200d♂️',
    'man_getting_haircut_medium_skin_tone': '💇🏽\u200d♂️',
    'man_getting_massage': '💆\u200d♂️',
    'man_getting_massage_dark_skin_tone': '💆🏿\u200d♂️',
    'man_getting_massage_light_skin_tone': '💆🏻\u200d♂️',
    'man_getting_massage_medium-dark_skin_tone': '💆🏾\u200d♂️',
    'man_getting_massage_medium-light_skin_tone': '💆🏼\u200d♂️',
    'man_getting_massage_medium_skin_tone': '💆🏽\u200d♂️', 'man_golfing':
    '🏌️\u200d♂️', 'man_golfing_dark_skin_tone': '🏌🏿\u200d♂️',
    'man_golfing_light_skin_tone': '🏌🏻\u200d♂️',
    'man_golfing_medium-dark_skin_tone': '🏌🏾\u200d♂️',
    'man_golfing_medium-light_skin_tone': '🏌🏼\u200d♂️',
    'man_golfing_medium_skin_tone': '🏌🏽\u200d♂️', 'man_guard': '💂\u200d♂️',
    'man_guard_dark_skin_tone': '💂🏿\u200d♂️', 'man_guard_light_skin_tone':
    '💂🏻\u200d♂️', 'man_guard_medium-dark_skin_tone': '💂🏾\u200d♂️',
    'man_guard_medium-light_skin_tone': '💂🏼\u200d♂️',
    'man_guard_medium_skin_tone': '💂🏽\u200d♂️', 'man_health_worker':
    '👨\u200d⚕️', 'man_health_worker_dark_skin_tone': '👨🏿\u200d⚕️',
    'man_health_worker_light_skin_tone': '👨🏻\u200d⚕️',
    'man_health_worker_medium-dark_skin_tone': '👨🏾\u200d⚕️',
    'man_health_worker_medium-light_skin_tone': '👨🏼\u200d⚕️',
    'man_health_worker_medium_skin_tone': '👨🏽\u200d⚕️',
    'man_in_lotus_position': '🧘\u200d♂️',
    'man_in_lotus_position_dark_skin_tone': '🧘🏿\u200d♂️',
    'man_in_lotus_position_light_skin_tone': '🧘🏻\u200d♂️',
    'man_in_lotus_position_medium-dark_skin_tone': '🧘🏾\u200d♂️',
    'man_in_lotus_position_medium-light_skin_tone': '🧘🏼\u200d♂️',
    'man_in_lotus_position_medium_skin_tone': '🧘🏽\u200d♂️',
    'man_in_manual_wheelchair': '👨\u200d🦽', 'man_in_motorized_wheelchair':
    '👨\u200d🦼', 'man_in_steamy_room': '🧖\u200d♂️',
    'man_in_steamy_room_dark_skin_tone': '🧖🏿\u200d♂️',
    'man_in_steamy_room_light_skin_tone': '🧖🏻\u200d♂️',
    'man_in_steamy_room_medium-dark_skin_tone': '🧖🏾\u200d♂️',
    'man_in_steamy_room_medium-light_skin_tone': '🧖🏼\u200d♂️',
    'man_in_steamy_room_medium_skin_tone': '🧖🏽\u200d♂️',
    'man_in_suit_levitating': '🕴', 'man_in_suit_levitating_dark_skin_tone':
    '🕴🏿', 'man_in_suit_levitating_light_skin_tone': '🕴🏻',
    'man_in_suit_levitating_medium-dark_skin_tone': '🕴🏾',
    'man_in_suit_levitating_medium-light_skin_tone': '🕴🏼',
    'man_in_suit_levitating_medium_skin_tone': '🕴🏽', 'man_in_tuxedo': '🤵',
    'man_in_tuxedo_dark_skin_tone': '🤵🏿', 'man_in_tuxedo_light_skin_tone':
    '🤵🏻', 'man_in_tuxedo_medium-dark_skin_tone': '🤵🏾',
    'man_in_tuxedo_medium-light_skin_tone': '🤵🏼',
    'man_in_tuxedo_medium_skin_tone': '🤵🏽', 'man_judge': '👨\u200d⚖️',
    'man_judge_dark_skin_tone': '👨🏿\u200d⚖️', 'man_judge_light_skin_tone':
    '👨🏻\u200d⚖️', 'man_judge_medium-dark_skin_tone': '👨🏾\u200d⚖️',
    'man_judge_medium-light_skin_tone': '👨🏼\u200d⚖️',
    'man_judge_medium_skin_tone': '👨🏽\u200d⚖️', 'man_juggling': '🤹\u200d♂️',
    'man_juggling_dark_skin_tone': '🤹🏿\u200d♂️',
    'man_juggling_light_skin_tone': '🤹🏻\u200d♂️',
    'man_juggling_medium-dark_skin_tone': '🤹🏾\u200d♂️',
    'man_juggling_medium-light_skin_tone': '🤹🏼\u200d♂️',
    'man_juggling_medium_skin_tone': '🤹🏽\u200d♂️', 'man_lifting_weights':
    '🏋️\u200d♂️', 'man_lifting_weights_dark_skin_tone': '🏋🏿\u200d♂️',
    'man_lifting_weights_light_skin_tone': '🏋🏻\u200d♂️',
    'man_lifting_weights_medium-dark_skin_tone': '🏋🏾\u200d♂️',
    'man_lifting_weights_medium-light_skin_tone': '🏋🏼\u200d♂️',
    'man_lifting_weights_medium_skin_tone': '🏋🏽\u200d♂️',
    'man_light_skin_tone': '👨🏻', 'man_mage': '🧙\u200d♂️',
    'man_mage_dark_skin_tone': '🧙🏿\u200d♂️', 'man_mage_light_skin_tone':
    '🧙🏻\u200d♂️', 'man_mage_medium-dark_skin_tone': '🧙🏾\u200d♂️',
    'man_mage_medium-light_skin_tone': '🧙🏼\u200d♂️',
    'man_mage_medium_skin_tone': '🧙🏽\u200d♂️', 'man_mechanic': '👨\u200d🔧',
    'man_mechanic_dark_skin_tone': '👨🏿\u200d🔧',
    'man_mechanic_light_skin_tone': '👨🏻\u200d🔧',
    'man_mechanic_medium-dark_skin_tone': '👨🏾\u200d🔧',
    'man_mechanic_medium-light_skin_tone': '👨🏼\u200d🔧',
    'man_mechanic_medium_skin_tone': '👨🏽\u200d🔧',
    'man_medium-dark_skin_tone': '👨🏾', 'man_medium-light_skin_tone': '👨🏼',
    'man_medium_skin_tone': '👨🏽', 'man_mountain_biking': '🚵\u200d♂️',
    'man_mountain_biking_dark_skin_tone': '🚵🏿\u200d♂️',
    'man_mountain_biking_light_skin_tone': '🚵🏻\u200d♂️',
    'man_mountain_biking_medium-dark_skin_tone': '🚵🏾\u200d♂️',
    'man_mountain_biking_medium-light_skin_tone': '🚵🏼\u200d♂️',
    'man_mountain_biking_medium_skin_tone': '🚵🏽\u200d♂️',
    'man_office_worker': '👨\u200d💼', 'man_office_worker_dark_skin_tone':
    '👨🏿\u200d💼', 'man_office_worker_light_skin_tone': '👨🏻\u200d💼',
    'man_office_worker_medium-dark_skin_tone': '👨🏾\u200d💼',
    'man_office_worker_medium-light_skin_tone': '👨🏼\u200d💼',
    'man_office_worker_medium_skin_tone': '👨🏽\u200d💼', 'man_pilot':
    '👨\u200d✈️', 'man_pilot_dark_skin_tone': '👨🏿\u200d✈️',
    'man_pilot_light_skin_tone': '👨🏻\u200d✈️',
    'man_pilot_medium-dark_skin_tone': '👨🏾\u200d✈️',
    'man_pilot_medium-light_skin_tone': '👨🏼\u200d✈️',
    'man_pilot_medium_skin_tone': '👨🏽\u200d✈️', 'man_playing_handball':
    '🤾\u200d♂️', 'man_playing_handball_dark_skin_tone': '🤾🏿\u200d♂️',
    'man_playing_handball_light_skin_tone': '🤾🏻\u200d♂️',
    'man_playing_handball_medium-dark_skin_tone': '🤾🏾\u200d♂️',
    'man_playing_handball_medium-light_skin_tone': '🤾🏼\u200d♂️',
    'man_playing_handball_medium_skin_tone': '🤾🏽\u200d♂️',
    'man_playing_water_polo': '🤽\u200d♂️',
    'man_playing_water_polo_dark_skin_tone': '🤽🏿\u200d♂️',
    'man_playing_water_polo_light_skin_tone': '🤽🏻\u200d♂️',
    'man_playing_water_polo_medium-dark_skin_tone': '🤽🏾\u200d♂️',
    'man_playing_water_polo_medium-light_skin_tone': '🤽🏼\u200d♂️',
    'man_playing_water_polo_medium_skin_tone': '🤽🏽\u200d♂️',
    'man_police_officer': '👮\u200d♂️', 'man_police_officer_dark_skin_tone':
    '👮🏿\u200d♂️', 'man_police_officer_light_skin_tone': '👮🏻\u200d♂️',
    'man_police_officer_medium-dark_skin_tone': '👮🏾\u200d♂️',
    'man_police_officer_medium-light_skin_tone': '👮🏼\u200d♂️',
    'man_police_officer_medium_skin_tone': '👮🏽\u200d♂️', 'man_pouting':
    '🙎\u200d♂️', 'man_pouting_dark_skin_tone': '🙎🏿\u200d♂️',
    'man_pouting_light_skin_tone': '🙎🏻\u200d♂️',
    'man_pouting_medium-dark_skin_tone': '🙎🏾\u200d♂️',
    'man_pouting_medium-light_skin_tone': '🙎🏼\u200d♂️',
    'man_pouting_medium_skin_tone': '🙎🏽\u200d♂️', 'man_raising_hand':
    '🙋\u200d♂️', 'man_raising_hand_dark_skin_tone': '🙋🏿\u200d♂️',
    'man_raising_hand_light_skin_tone': '🙋🏻\u200d♂️',
    'man_raising_hand_medium-dark_skin_tone': '🙋🏾\u200d♂️',
    'man_raising_hand_medium-light_skin_tone': '🙋🏼\u200d♂️',
    'man_raising_hand_medium_skin_tone': '🙋🏽\u200d♂️', 'man_rowing_boat':
    '🚣\u200d♂️', 'man_rowing_boat_dark_skin_tone': '🚣🏿\u200d♂️',
    'man_rowing_boat_light_skin_tone': '🚣🏻\u200d♂️',
    'man_rowing_boat_medium-dark_skin_tone': '🚣🏾\u200d♂️',
    'man_rowing_boat_medium-light_skin_tone': '🚣🏼\u200d♂️',
    'man_rowing_boat_medium_skin_tone': '🚣🏽\u200d♂️', 'man_running':
    '🏃\u200d♂️', 'man_running_dark_skin_tone': '🏃🏿\u200d♂️',
    'man_running_light_skin_tone': '🏃🏻\u200d♂️',
    'man_running_medium-dark_skin_tone': '🏃🏾\u200d♂️',
    'man_running_medium-light_skin_tone': '🏃🏼\u200d♂️',
    'man_running_medium_skin_tone': '🏃🏽\u200d♂️', 'man_scientist':
    '👨\u200d🔬', 'man_scientist_dark_skin_tone': '👨🏿\u200d🔬',
    'man_scientist_light_skin_tone': '👨🏻\u200d🔬',
    'man_scientist_medium-dark_skin_tone': '👨🏾\u200d🔬',
    'man_scientist_medium-light_skin_tone': '👨🏼\u200d🔬',
    'man_scientist_medium_skin_tone': '👨🏽\u200d🔬', 'man_shrugging':
    '🤷\u200d♂️', 'man_shrugging_dark_skin_tone': '🤷🏿\u200d♂️',
    'man_shrugging_light_skin_tone': '🤷🏻\u200d♂️',
    'man_shrugging_medium-dark_skin_tone': '🤷🏾\u200d♂️',
    'man_shrugging_medium-light_skin_tone': '🤷🏼\u200d♂️',
    'man_shrugging_medium_skin_tone': '🤷🏽\u200d♂️', 'man_singer':
    '👨\u200d🎤', 'man_singer_dark_skin_tone': '👨🏿\u200d🎤',
    'man_singer_light_skin_tone': '👨🏻\u200d🎤',
    'man_singer_medium-dark_skin_tone': '👨🏾\u200d🎤',
    'man_singer_medium-light_skin_tone': '👨🏼\u200d🎤',
    'man_singer_medium_skin_tone': '👨🏽\u200d🎤', 'man_student': '👨\u200d🎓',
    'man_student_dark_skin_tone': '👨🏿\u200d🎓',
    'man_student_light_skin_tone': '👨🏻\u200d🎓',
    'man_student_medium-dark_skin_tone': '👨🏾\u200d🎓',
    'man_student_medium-light_skin_tone': '👨🏼\u200d🎓',
    'man_student_medium_skin_tone': '👨🏽\u200d🎓', 'man_surfing': '🏄\u200d♂️',
    'man_surfing_dark_skin_tone': '🏄🏿\u200d♂️',
    'man_surfing_light_skin_tone': '🏄🏻\u200d♂️',
    'man_surfing_medium-dark_skin_tone': '🏄🏾\u200d♂️',
    'man_surfing_medium-light_skin_tone': '🏄🏼\u200d♂️',
    'man_surfing_medium_skin_tone': '🏄🏽\u200d♂️', 'man_swimming':
    '🏊\u200d♂️', 'man_swimming_dark_skin_tone': '🏊🏿\u200d♂️',
    'man_swimming_light_skin_tone': '🏊🏻\u200d♂️',
    'man_swimming_medium-dark_skin_tone': '🏊🏾\u200d♂️',
    'man_swimming_medium-light_skin_tone': '🏊🏼\u200d♂️',
    'man_swimming_medium_skin_tone': '🏊🏽\u200d♂️', 'man_teacher':
    '👨\u200d🏫', 'man_teacher_dark_skin_tone': '👨🏿\u200d🏫',
    'man_teacher_light_skin_tone': '👨🏻\u200d🏫',
    'man_teacher_medium-dark_skin_tone': '👨🏾\u200d🏫',
    'man_teacher_medium-light_skin_tone': '👨🏼\u200d🏫',
    'man_teacher_medium_skin_tone': '👨🏽\u200d🏫', 'man_technologist':
    '👨\u200d💻', 'man_technologist_dark_skin_tone': '👨🏿\u200d💻',
    'man_technologist_light_skin_tone': '👨🏻\u200d💻',
    'man_technologist_medium-dark_skin_tone': '👨🏾\u200d💻',
    'man_technologist_medium-light_skin_tone': '👨🏼\u200d💻',
    'man_technologist_medium_skin_tone': '👨🏽\u200d💻', 'man_tipping_hand':
    '💁\u200d♂️', 'man_tipping_hand_dark_skin_tone': '💁🏿\u200d♂️',
    'man_tipping_hand_light_skin_tone': '💁🏻\u200d♂️',
    'man_tipping_hand_medium-dark_skin_tone': '💁🏾\u200d♂️',
    'man_tipping_hand_medium-light_skin_tone': '💁🏼\u200d♂️',
    'man_tipping_hand_medium_skin_tone': '💁🏽\u200d♂️', 'man_vampire':
    '🧛\u200d♂️', 'man_vampire_dark_skin_tone': '🧛🏿\u200d♂️',
    'man_vampire_light_skin_tone': '🧛🏻\u200d♂️',
    'man_vampire_medium-dark_skin_tone': '🧛🏾\u200d♂️',
    'man_vampire_medium-light_skin_tone': '🧛🏼\u200d♂️',
    'man_vampire_medium_skin_tone': '🧛🏽\u200d♂️', 'man_walking':
    '🚶\u200d♂️', 'man_walking_dark_skin_tone': '🚶🏿\u200d♂️',
    'man_walking_light_skin_tone': '🚶🏻\u200d♂️',
    'man_walking_medium-dark_skin_tone': '🚶🏾\u200d♂️',
    'man_walking_medium-light_skin_tone': '🚶🏼\u200d♂️',
    'man_walking_medium_skin_tone': '🚶🏽\u200d♂️', 'man_wearing_turban':
    '👳\u200d♂️', 'man_wearing_turban_dark_skin_tone': '👳🏿\u200d♂️',
    'man_wearing_turban_light_skin_tone': '👳🏻\u200d♂️',
    'man_wearing_turban_medium-dark_skin_tone': '👳🏾\u200d♂️',
    'man_wearing_turban_medium-light_skin_tone': '👳🏼\u200d♂️',
    'man_wearing_turban_medium_skin_tone': '👳🏽\u200d♂️',
    'man_with_probing_cane': '👨\u200d🦯', 'man_with_chinese_cap': '👲',
    'man_with_chinese_cap_dark_skin_tone': '👲🏿',
    'man_with_chinese_cap_light_skin_tone': '👲🏻',
    'man_with_chinese_cap_medium-dark_skin_tone': '👲🏾',
    'man_with_chinese_cap_medium-light_skin_tone': '👲🏼',
    'man_with_chinese_cap_medium_skin_tone': '👲🏽', 'man_zombie':
    '🧟\u200d♂️', 'mango': '🥭', 'mantelpiece_clock': '🕰',
    'manual_wheelchair': '🦽', 'man’s_shoe': '👞', 'map_of_japan': '🗾',
    'maple_leaf': '🍁', 'martial_arts_uniform': '🥋', 'mate': '🧉',
    'meat_on_bone': '🍖', 'mechanical_arm': '🦾', 'mechanical_leg': '🦿',
    'medical_symbol': '⚕', 'megaphone': '📣', 'melon': '🍈', 'memo': '📝',
    'men_with_bunny_ears': '👯\u200d♂️', 'men_wrestling': '🤼\u200d♂️',
    'menorah': '🕎', 'men’s_room': '🚹', 'mermaid': '🧜\u200d♀️',
    'mermaid_dark_skin_tone': '🧜🏿\u200d♀️', 'mermaid_light_skin_tone':
    '🧜🏻\u200d♀️', 'mermaid_medium-dark_skin_tone': '🧜🏾\u200d♀️',
    'mermaid_medium-light_skin_tone': '🧜🏼\u200d♀️',
    'mermaid_medium_skin_tone': '🧜🏽\u200d♀️', 'merman': '🧜\u200d♂️',
    'merman_dark_skin_tone': '🧜🏿\u200d♂️', 'merman_light_skin_tone':
    '🧜🏻\u200d♂️', 'merman_medium-dark_skin_tone': '🧜🏾\u200d♂️',
    'merman_medium-light_skin_tone': '🧜🏼\u200d♂️',
    'merman_medium_skin_tone': '🧜🏽\u200d♂️', 'merperson': '🧜',
    'merperson_dark_skin_tone': '🧜🏿', 'merperson_light_skin_tone': '🧜🏻',
    'merperson_medium-dark_skin_tone': '🧜🏾',
    'merperson_medium-light_skin_tone': '🧜🏼', 'merperson_medium_skin_tone':
    '🧜🏽', 'metro': '🚇', 'microbe': '🦠', 'microphone': '🎤', 'microscope':
    '🔬', 'middle_finger': '🖕', 'middle_finger_dark_skin_tone': '🖕🏿',
    'middle_finger_light_skin_tone': '🖕🏻',
    'middle_finger_medium-dark_skin_tone': '🖕🏾',
    'middle_finger_medium-light_skin_tone': '🖕🏼',
    'middle_finger_medium_skin_tone': '🖕🏽', 'military_medal': '🎖',
    'milky_way': '🌌', 'minibus': '🚐', 'moai': '🗿', 'mobile_phone': '📱',
    'mobile_phone_off': '📴', 'mobile_phone_with_arrow': '📲',
    'money-mouth_face': '🤑', 'money_bag': '💰', 'money_with_wings': '💸',
    'monkey': '🐒', 'monkey_face': '🐵', 'monorail': '🚝', 'moon_cake': '🥮',
    'moon_viewing_ceremony': '🎑', 'mosque': '🕌', 'mosquito': '🦟',
    'motor_boat': '🛥', 'motor_scooter': '🛵', 'motorcycle': '🏍',
    'motorized_wheelchair': '🦼', 'motorway': '🛣', 'mount_fuji': '🗻',
    'mountain': '⛰', 'mountain_cableway': '🚠', 'mountain_railway': '🚞',
    'mouse': '🐭', 'mouse_face': '🐭', 'mouth': '👄', 'movie_camera': '🎥',
    'mushroom': '🍄', 'musical_keyboard': '🎹', 'musical_note': '🎵',
    'musical_notes': '🎶', 'musical_score': '🎼', 'muted_speaker': '🔇',
    'nail_polish': '💅', 'nail_polish_dark_skin_tone': '💅🏿',
    'nail_polish_light_skin_tone': '💅🏻',
    'nail_polish_medium-dark_skin_tone': '💅🏾',
    'nail_polish_medium-light_skin_tone': '💅🏼',
    'nail_polish_medium_skin_tone': '💅🏽', 'name_badge': '📛',
    'national_park': '🏞', 'nauseated_face': '🤢', 'nazar_amulet': '🧿',
    'necktie': '👔', 'nerd_face': '🤓', 'neutral_face': '😐', 'new_moon': '🌑',
    'new_moon_face': '🌚', 'newspaper': '📰', 'next_track_button': '⏭',
    'night_with_stars': '🌃', 'nine-thirty': '🕤', 'nine_o’clock': '🕘',
    'no_bicycles': '🚳', 'no_entry': '⛔', 'no_littering': '🚯',
    'no_mobile_phones': '📵', 'no_one_under_eighteen': '🔞', 'no_pedestrians':
    '🚷', 'no_smoking': '🚭', 'non-potable_water': '🚱', 'nose': '👃',
    'nose_dark_skin_tone': '👃🏿', 'nose_light_skin_tone': '👃🏻',
    'nose_medium-dark_skin_tone': '👃🏾', 'nose_medium-light_skin_tone': '👃🏼',
    'nose_medium_skin_tone': '👃🏽', 'notebook': '📓',
    'notebook_with_decorative_cover': '📔', 'nut_and_bolt': '🔩', 'octopus':
    '🐙', 'oden': '🍢', 'office_building': '🏢', 'ogre': '👹', 'oil_drum': '🛢',
    'old_key': '🗝', 'old_man': '👴', 'old_man_dark_skin_tone': '👴🏿',
    'old_man_light_skin_tone': '👴🏻', 'old_man_medium-dark_skin_tone': '👴🏾',
    'old_man_medium-light_skin_tone': '👴🏼', 'old_man_medium_skin_tone':
    '👴🏽', 'old_woman': '👵', 'old_woman_dark_skin_tone': '👵🏿',
    'old_woman_light_skin_tone': '👵🏻', 'old_woman_medium-dark_skin_tone':
    '👵🏾', 'old_woman_medium-light_skin_tone': '👵🏼',
    'old_woman_medium_skin_tone': '👵🏽', 'older_adult': '🧓',
    'older_adult_dark_skin_tone': '🧓🏿', 'older_adult_light_skin_tone': '🧓🏻',
    'older_adult_medium-dark_skin_tone': '🧓🏾',
    'older_adult_medium-light_skin_tone': '🧓🏼',
    'older_adult_medium_skin_tone': '🧓🏽', 'om': '🕉', 'oncoming_automobile':
    '🚘', 'oncoming_bus': '🚍', 'oncoming_fist': '👊',
    'oncoming_fist_dark_skin_tone': '👊🏿', 'oncoming_fist_light_skin_tone':
    '👊🏻', 'oncoming_fist_medium-dark_skin_tone': '👊🏾',
    'oncoming_fist_medium-light_skin_tone': '👊🏼',
    'oncoming_fist_medium_skin_tone': '👊🏽', 'oncoming_police_car': '🚔',
    'oncoming_taxi': '🚖', 'one-piece_swimsuit': '🩱', 'one-thirty': '🕜',
    'one_o’clock': '🕐', 'onion': '🧅', 'open_book': '📖', 'open_file_folder':
    '📂', 'open_hands': '👐', 'open_hands_dark_skin_tone': '👐🏿',
    'open_hands_light_skin_tone': '👐🏻', 'open_hands_medium-dark_skin_tone':
    '👐🏾', 'open_hands_medium-light_skin_tone': '👐🏼',
    'open_hands_medium_skin_tone': '👐🏽', 'open_mailbox_with_lowered_flag':
    '📭', 'open_mailbox_with_raised_flag': '📬', 'optical_disk': '💿',
    'orange_book': '📙', 'orange_circle': '🟠', 'orange_heart': '🧡',
    'orange_square': '🟧', 'orangutan': '🦧', 'orthodox_cross': '☦', 'otter':
    '🦦', 'outbox_tray': '📤', 'owl': '🦉', 'ox': '🐂', 'oyster': '🦪',
    'package': '📦', 'page_facing_up': '📄', 'page_with_curl': '📃', 'pager':
    '📟', 'paintbrush': '🖌', 'palm_tree': '🌴', 'palms_up_together': '🤲',
    'palms_up_together_dark_skin_tone': '🤲🏿',
    'palms_up_together_light_skin_tone': '🤲🏻',
    'palms_up_together_medium-dark_skin_tone': '🤲🏾',
    'palms_up_together_medium-light_skin_tone': '🤲🏼',
    'palms_up_together_medium_skin_tone': '🤲🏽', 'pancakes': '🥞',
    'panda_face': '🐼', 'paperclip': '📎', 'parrot': '🦜',
    'part_alternation_mark': '〽', 'party_popper': '🎉', 'partying_face': '🥳',
    'passenger_ship': '🛳', 'passport_control': '🛂', 'pause_button': '⏸',
    'paw_prints': '🐾', 'peace_symbol': '☮', 'peach': '🍑', 'peacock': '🦚',
    'peanuts': '🥜', 'pear': '🍐', 'pen': '🖊', 'pencil': '📝', 'penguin': '🐧',
    'pensive_face': '😔', 'people_holding_hands': '🧑\u200d🤝\u200d🧑',
    'people_with_bunny_ears': '👯', 'people_wrestling': '🤼',
    'performing_arts': '🎭', 'persevering_face': '😣', 'person_biking': '🚴',
    'person_biking_dark_skin_tone': '🚴🏿', 'person_biking_light_skin_tone':
    '🚴🏻', 'person_biking_medium-dark_skin_tone': '🚴🏾',
    'person_biking_medium-light_skin_tone': '🚴🏼',
    'person_biking_medium_skin_tone': '🚴🏽', 'person_bouncing_ball': '⛹',
    'person_bouncing_ball_dark_skin_tone': '⛹🏿',
    'person_bouncing_ball_light_skin_tone': '⛹🏻',
    'person_bouncing_ball_medium-dark_skin_tone': '⛹🏾',
    'person_bouncing_ball_medium-light_skin_tone': '⛹🏼',
    'person_bouncing_ball_medium_skin_tone': '⛹🏽', 'person_bowing': '🙇',
    'person_bowing_dark_skin_tone': '🙇🏿', 'person_bowing_light_skin_tone':
    '🙇🏻', 'person_bowing_medium-dark_skin_tone': '🙇🏾',
    'person_bowing_medium-light_skin_tone': '🙇🏼',
    'person_bowing_medium_skin_tone': '🙇🏽', 'person_cartwheeling': '🤸',
    'person_cartwheeling_dark_skin_tone': '🤸🏿',
    'person_cartwheeling_light_skin_tone': '🤸🏻',
    'person_cartwheeling_medium-dark_skin_tone': '🤸🏾',
    'person_cartwheeling_medium-light_skin_tone': '🤸🏼',
    'person_cartwheeling_medium_skin_tone': '🤸🏽', 'person_climbing': '🧗',
    'person_climbing_dark_skin_tone': '🧗🏿',
    'person_climbing_light_skin_tone': '🧗🏻',
    'person_climbing_medium-dark_skin_tone': '🧗🏾',
    'person_climbing_medium-light_skin_tone': '🧗🏼',
    'person_climbing_medium_skin_tone': '🧗🏽', 'person_facepalming': '🤦',
    'person_facepalming_dark_skin_tone': '🤦🏿',
    'person_facepalming_light_skin_tone': '🤦🏻',
    'person_facepalming_medium-dark_skin_tone': '🤦🏾',
    'person_facepalming_medium-light_skin_tone': '🤦🏼',
    'person_facepalming_medium_skin_tone': '🤦🏽', 'person_fencing': '🤺',
    'person_frowning': '🙍', 'person_frowning_dark_skin_tone': '🙍🏿',
    'person_frowning_light_skin_tone': '🙍🏻',
    'person_frowning_medium-dark_skin_tone': '🙍🏾',
    'person_frowning_medium-light_skin_tone': '🙍🏼',
    'person_frowning_medium_skin_tone': '🙍🏽', 'person_gesturing_no': '🙅',
    'person_gesturing_no_dark_skin_tone': '🙅🏿',
    'person_gesturing_no_light_skin_tone': '🙅🏻',
    'person_gesturing_no_medium-dark_skin_tone': '🙅🏾',
    'person_gesturing_no_medium-light_skin_tone': '🙅🏼',
    'person_gesturing_no_medium_skin_tone': '🙅🏽', 'person_gesturing_ok':
    '🙆', 'person_gesturing_ok_dark_skin_tone': '🙆🏿',
    'person_gesturing_ok_light_skin_tone': '🙆🏻',
    'person_gesturing_ok_medium-dark_skin_tone': '🙆🏾',
    'person_gesturing_ok_medium-light_skin_tone': '🙆🏼',
    'person_gesturing_ok_medium_skin_tone': '🙆🏽', 'person_getting_haircut':
    '💇', 'person_getting_haircut_dark_skin_tone': '💇🏿',
    'person_getting_haircut_light_skin_tone': '💇🏻',
    'person_getting_haircut_medium-dark_skin_tone': '💇🏾',
    'person_getting_haircut_medium-light_skin_tone': '💇🏼',
    'person_getting_haircut_medium_skin_tone': '💇🏽',
    'person_getting_massage': '💆', 'person_getting_massage_dark_skin_tone':
    '💆🏿', 'person_getting_massage_light_skin_tone': '💆🏻',
    'person_getting_massage_medium-dark_skin_tone': '💆🏾',
    'person_getting_massage_medium-light_skin_tone': '💆🏼',
    'person_getting_massage_medium_skin_tone': '💆🏽', 'person_golfing': '🏌',
    'person_golfing_dark_skin_tone': '🏌🏿', 'person_golfing_light_skin_tone':
    '🏌🏻', 'person_golfing_medium-dark_skin_tone': '🏌🏾',
    'person_golfing_medium-light_skin_tone': '🏌🏼',
    'person_golfing_medium_skin_tone': '🏌🏽', 'person_in_bed': '🛌',
    'person_in_bed_dark_skin_tone': '🛌🏿', 'person_in_bed_light_skin_tone':
    '🛌🏻', 'person_in_bed_medium-dark_skin_tone': '🛌🏾',
    'person_in_bed_medium-light_skin_tone': '🛌🏼',
    'person_in_bed_medium_skin_tone': '🛌🏽', 'person_in_lotus_position': '🧘',
    'person_in_lotus_position_dark_skin_tone': '🧘🏿',
    'person_in_lotus_position_light_skin_tone': '🧘🏻',
    'person_in_lotus_position_medium-dark_skin_tone': '🧘🏾',
    'person_in_lotus_position_medium-light_skin_tone': '🧘🏼',
    'person_in_lotus_position_medium_skin_tone': '🧘🏽',
    'person_in_steamy_room': '🧖', 'person_in_steamy_room_dark_skin_tone':
    '🧖🏿', 'person_in_steamy_room_light_skin_tone': '🧖🏻',
    'person_in_steamy_room_medium-dark_skin_tone': '🧖🏾',
    'person_in_steamy_room_medium-light_skin_tone': '🧖🏼',
    'person_in_steamy_room_medium_skin_tone': '🧖🏽', 'person_juggling': '🤹',
    'person_juggling_dark_skin_tone': '🤹🏿',
    'person_juggling_light_skin_tone': '🤹🏻',
    'person_juggling_medium-dark_skin_tone': '🤹🏾',
    'person_juggling_medium-light_skin_tone': '🤹🏼',
    'person_juggling_medium_skin_tone': '🤹🏽', 'person_kneeling': '🧎',
    'person_lifting_weights': '🏋', 'person_lifting_weights_dark_skin_tone':
    '🏋🏿', 'person_lifting_weights_light_skin_tone': '🏋🏻',
    'person_lifting_weights_medium-dark_skin_tone': '🏋🏾',
    'person_lifting_weights_medium-light_skin_tone': '🏋🏼',
    'person_lifting_weights_medium_skin_tone': '🏋🏽',
    'person_mountain_biking': '🚵', 'person_mountain_biking_dark_skin_tone':
    '🚵🏿', 'person_mountain_biking_light_skin_tone': '🚵🏻',
    'person_mountain_biking_medium-dark_skin_tone': '🚵🏾',
    'person_mountain_biking_medium-light_skin_tone': '🚵🏼',
    'person_mountain_biking_medium_skin_tone': '🚵🏽',
    'person_playing_handball': '🤾',
    'person_playing_handball_dark_skin_tone': '🤾🏿',
    'person_playing_handball_light_skin_tone': '🤾🏻',
    'person_playing_handball_medium-dark_skin_tone': '🤾🏾',
    'person_playing_handball_medium-light_skin_tone': '🤾🏼',
    'person_playing_handball_medium_skin_tone': '🤾🏽',
    'person_playing_water_polo': '🤽',
    'person_playing_water_polo_dark_skin_tone': '🤽🏿',
    'person_playing_water_polo_light_skin_tone': '🤽🏻',
    'person_playing_water_polo_medium-dark_skin_tone': '🤽🏾',
    'person_playing_water_polo_medium-light_skin_tone': '🤽🏼',
    'person_playing_water_polo_medium_skin_tone': '🤽🏽', 'person_pouting':
    '🙎', 'person_pouting_dark_skin_tone': '🙎🏿',
    'person_pouting_light_skin_tone': '🙎🏻',
    'person_pouting_medium-dark_skin_tone': '🙎🏾',
    'person_pouting_medium-light_skin_tone': '🙎🏼',
    'person_pouting_medium_skin_tone': '🙎🏽', 'person_raising_hand': '🙋',
    'person_raising_hand_dark_skin_tone': '🙋🏿',
    'person_raising_hand_light_skin_tone': '🙋🏻',
    'person_raising_hand_medium-dark_skin_tone': '🙋🏾',
    'person_raising_hand_medium-light_skin_tone': '🙋🏼',
    'person_raising_hand_medium_skin_tone': '🙋🏽', 'person_rowing_boat': '🚣',
    'person_rowing_boat_dark_skin_tone': '🚣🏿',
    'person_rowing_boat_light_skin_tone': '🚣🏻',
    'person_rowing_boat_medium-dark_skin_tone': '🚣🏾',
    'person_rowing_boat_medium-light_skin_tone': '🚣🏼',
    'person_rowing_boat_medium_skin_tone': '🚣🏽', 'person_running': '🏃',
    'person_running_dark_skin_tone': '🏃🏿', 'person_running_light_skin_tone':
    '🏃🏻', 'person_running_medium-dark_skin_tone': '🏃🏾',
    'person_running_medium-light_skin_tone': '🏃🏼',
    'person_running_medium_skin_tone': '🏃🏽', 'person_shrugging': '🤷',
    'person_shrugging_dark_skin_tone': '🤷🏿',
    'person_shrugging_light_skin_tone': '🤷🏻',
    'person_shrugging_medium-dark_skin_tone': '🤷🏾',
    'person_shrugging_medium-light_skin_tone': '🤷🏼',
    'person_shrugging_medium_skin_tone': '🤷🏽', 'person_standing': '🧍',
    'person_surfing': '🏄', 'person_surfing_dark_skin_tone': '🏄🏿',
    'person_surfing_light_skin_tone': '🏄🏻',
    'person_surfing_medium-dark_skin_tone': '🏄🏾',
    'person_surfing_medium-light_skin_tone': '🏄🏼',
    'person_surfing_medium_skin_tone': '🏄🏽', 'person_swimming': '🏊',
    'person_swimming_dark_skin_tone': '🏊🏿',
    'person_swimming_light_skin_tone': '🏊🏻',
    'person_swimming_medium-dark_skin_tone': '🏊🏾',
    'person_swimming_medium-light_skin_tone': '🏊🏼',
    'person_swimming_medium_skin_tone': '🏊🏽', 'person_taking_bath': '🛀',
    'person_taking_bath_dark_skin_tone': '🛀🏿',
    'person_taking_bath_light_skin_tone': '🛀🏻',
    'person_taking_bath_medium-dark_skin_tone': '🛀🏾',
    'person_taking_bath_medium-light_skin_tone': '🛀🏼',
    'person_taking_bath_medium_skin_tone': '🛀🏽', 'person_tipping_hand': '💁',
    'person_tipping_hand_dark_skin_tone': '💁🏿',
    'person_tipping_hand_light_skin_tone': '💁🏻',
    'person_tipping_hand_medium-dark_skin_tone': '💁🏾',
    'person_tipping_hand_medium-light_skin_tone': '💁🏼',
    'person_tipping_hand_medium_skin_tone': '💁🏽', 'person_walking': '🚶',
    'person_walking_dark_skin_tone': '🚶🏿', 'person_walking_light_skin_tone':
    '🚶🏻', 'person_walking_medium-dark_skin_tone': '🚶🏾',
    'person_walking_medium-light_skin_tone': '🚶🏼',
    'person_walking_medium_skin_tone': '🚶🏽', 'person_wearing_turban': '👳',
    'person_wearing_turban_dark_skin_tone': '👳🏿',
    'person_wearing_turban_light_skin_tone': '👳🏻',
    'person_wearing_turban_medium-dark_skin_tone': '👳🏾',
    'person_wearing_turban_medium-light_skin_tone': '👳🏼',
    'person_wearing_turban_medium_skin_tone': '👳🏽', 'petri_dish': '🧫',
    'pick': '⛏', 'pie': '🥧', 'pig': '🐷', 'pig_face': '🐷', 'pig_nose': '🐽',
    'pile_of_poo': '💩', 'pill': '💊', 'pinching_hand': '🤏',
    'pine_decoration': '🎍', 'pineapple': '🍍', 'ping_pong': '🏓',
    'pirate_flag': '🏴\u200d☠️', 'pistol': '🔫', 'pizza': '🍕',
    'place_of_worship': '🛐', 'play_button': '▶', 'play_or_pause_button':
    '⏯', 'pleading_face': '🥺', 'police_car': '🚓', 'police_car_light': '🚨',
    'police_officer': '👮', 'police_officer_dark_skin_tone': '👮🏿',
    'police_officer_light_skin_tone': '👮🏻',
    'police_officer_medium-dark_skin_tone': '👮🏾',
    'police_officer_medium-light_skin_tone': '👮🏼',
    'police_officer_medium_skin_tone': '👮🏽', 'poodle': '🐩', 'pool_8_ball':
    '🎱', 'popcorn': '🍿', 'post_office': '🏣', 'postal_horn': '📯', 'postbox':
    '📮', 'pot_of_food': '🍲', 'potable_water': '🚰', 'potato': '🥔',
    'poultry_leg': '🍗', 'pound_banknote': '💷', 'pouting_cat_face': '😾',
    'pouting_face': '😡', 'prayer_beads': '📿', 'pregnant_woman': '🤰',
    'pregnant_woman_dark_skin_tone': '🤰🏿', 'pregnant_woman_light_skin_tone':
    '🤰🏻', 'pregnant_woman_medium-dark_skin_tone': '🤰🏾',
    'pregnant_woman_medium-light_skin_tone': '🤰🏼',
    'pregnant_woman_medium_skin_tone': '🤰🏽', 'pretzel': '🥨', 'probing_cane':
    '🦯', 'prince': '🤴', 'prince_dark_skin_tone': '🤴🏿',
    'prince_light_skin_tone': '🤴🏻', 'prince_medium-dark_skin_tone': '🤴🏾',
    'prince_medium-light_skin_tone': '🤴🏼', 'prince_medium_skin_tone': '🤴🏽',
    'princess': '👸', 'princess_dark_skin_tone': '👸🏿',
    'princess_light_skin_tone': '👸🏻', 'princess_medium-dark_skin_tone':
    '👸🏾', 'princess_medium-light_skin_tone': '👸🏼',
    'princess_medium_skin_tone': '👸🏽', 'printer': '🖨', 'prohibited': '🚫',
    'purple_circle': '🟣', 'purple_heart': '💜', 'purple_square': '🟪',
    'purse': '👛', 'pushpin': '📌', 'question_mark': '❓', 'rabbit': '🐰',
    'rabbit_face': '🐰', 'raccoon': '🦝', 'racing_car': '🏎', 'radio': '📻',
    'radio_button': '🔘', 'radioactive': '☢', 'railway_car': '🚃',
    'railway_track': '🛤', 'rainbow': '🌈', 'rainbow_flag': '🏳️\u200d🌈',
    'raised_back_of_hand': '🤚', 'raised_back_of_hand_dark_skin_tone': '🤚🏿',
    'raised_back_of_hand_light_skin_tone': '🤚🏻',
    'raised_back_of_hand_medium-dark_skin_tone': '🤚🏾',
    'raised_back_of_hand_medium-light_skin_tone': '🤚🏼',
    'raised_back_of_hand_medium_skin_tone': '🤚🏽', 'raised_fist': '✊',
    'raised_fist_dark_skin_tone': '✊🏿', 'raised_fist_light_skin_tone': '✊🏻',
    'raised_fist_medium-dark_skin_tone': '✊🏾',
    'raised_fist_medium-light_skin_tone': '✊🏼',
    'raised_fist_medium_skin_tone': '✊🏽', 'raised_hand': '✋',
    'raised_hand_dark_skin_tone': '✋🏿', 'raised_hand_light_skin_tone': '✋🏻',
    'raised_hand_medium-dark_skin_tone': '✋🏾',
    'raised_hand_medium-light_skin_tone': '✋🏼',
    'raised_hand_medium_skin_tone': '✋🏽', 'raising_hands': '🙌',
    'raising_hands_dark_skin_tone': '🙌🏿', 'raising_hands_light_skin_tone':
    '🙌🏻', 'raising_hands_medium-dark_skin_tone': '🙌🏾',
    'raising_hands_medium-light_skin_tone': '🙌🏼',
    'raising_hands_medium_skin_tone': '🙌🏽', 'ram': '🐏', 'rat': '🐀', 'razor':
    '🪒', 'ringed_planet': '🪐', 'receipt': '🧾', 'record_button': '⏺',
    'recycling_symbol': '♻', 'red_apple': '🍎', 'red_circle': '🔴',
    'red_envelope': '🧧', 'red_hair': '🦰', 'red-haired_man': '👨\u200d🦰',
    'red-haired_woman': '👩\u200d🦰', 'red_heart': '❤', 'red_paper_lantern':
    '🏮', 'red_square': '🟥', 'red_triangle_pointed_down': '🔻',
    'red_triangle_pointed_up': '🔺', 'registered': '®', 'relieved_face': '😌',
    'reminder_ribbon': '🎗', 'repeat_button': '🔁', 'repeat_single_button':
    '🔂', 'rescue_worker’s_helmet': '⛑', 'restroom': '🚻', 'reverse_button':
    '◀', 'revolving_hearts': '💞', 'rhinoceros': '🦏', 'ribbon': '🎀',
    'rice_ball': '🍙', 'rice_cracker': '🍘', 'right-facing_fist': '🤜',
    'right-facing_fist_dark_skin_tone': '🤜🏿',
    'right-facing_fist_light_skin_tone': '🤜🏻',
    'right-facing_fist_medium-dark_skin_tone': '🤜🏾',
    'right-facing_fist_medium-light_skin_tone': '🤜🏼',
    'right-facing_fist_medium_skin_tone': '🤜🏽', 'right_anger_bubble': '🗯',
    'right_arrow': '➡', 'right_arrow_curving_down': '⤵',
    'right_arrow_curving_left': '↩', 'right_arrow_curving_up': '⤴', 'ring':
    '💍', 'roasted_sweet_potato': '🍠', 'robot_face': '🤖', 'rocket': '🚀',
    'roll_of_paper': '🧻', 'rolled-up_newspaper': '🗞', 'roller_coaster': '🎢',
    'rolling_on_the_floor_laughing': '🤣', 'rooster': '🐓', 'rose': '🌹',
    'rosette': '🏵', 'round_pushpin': '📍', 'rugby_football': '🏉',
    'running_shirt': '🎽', 'running_shoe': '👟', 'sad_but_relieved_face': '😥',
    'safety_pin': '🧷', 'safety_vest': '🦺', 'salt': '🧂', 'sailboat': '⛵',
    'sake': '🍶', 'sandwich': '🥪', 'sari': '🥻', 'satellite': '📡',
    'satellite_antenna': '📡', 'sauropod': '🦕', 'saxophone': '🎷', 'scarf':
    '🧣', 'school': '🏫', 'school_backpack': '🎒', 'scissors': '✂', 'scorpion':
    '🦂', 'scroll': '📜', 'seat': '💺', 'see-no-evil_monkey': '🙈', 'seedling':
    '🌱', 'selfie': '🤳', 'selfie_dark_skin_tone': '🤳🏿',
    'selfie_light_skin_tone': '🤳🏻', 'selfie_medium-dark_skin_tone': '🤳🏾',
    'selfie_medium-light_skin_tone': '🤳🏼', 'selfie_medium_skin_tone': '🤳🏽',
    'service_dog': '🐕\u200d🦺', 'seven-thirty': '🕢', 'seven_o’clock': '🕖',
    'shallow_pan_of_food': '🥘', 'shamrock': '☘', 'shark': '🦈', 'shaved_ice':
    '🍧', 'sheaf_of_rice': '🌾', 'shield': '🛡', 'shinto_shrine': '⛩', 'ship':
    '🚢', 'shooting_star': '🌠', 'shopping_bags': '🛍', 'shopping_cart': '🛒',
    'shortcake': '🍰', 'shorts': '🩳', 'shower': '🚿', 'shrimp': '🦐',
    'shuffle_tracks_button': '🔀', 'shushing_face': '🤫', 'sign_of_the_horns':
    '🤘', 'sign_of_the_horns_dark_skin_tone': '🤘🏿',
    'sign_of_the_horns_light_skin_tone': '🤘🏻',
    'sign_of_the_horns_medium-dark_skin_tone': '🤘🏾',
    'sign_of_the_horns_medium-light_skin_tone': '🤘🏼',
    'sign_of_the_horns_medium_skin_tone': '🤘🏽', 'six-thirty': '🕡',
    'six_o’clock': '🕕', 'skateboard': '🛹', 'skier': '⛷', 'skis': '🎿',
    'skull': '💀', 'skull_and_crossbones': '☠', 'skunk': '🦨', 'sled': '🛷',
    'sleeping_face': '😴', 'sleepy_face': '😪', 'slightly_frowning_face': '🙁',
    'slightly_smiling_face': '🙂', 'slot_machine': '🎰', 'sloth': '🦥',
    'small_airplane': '🛩', 'small_blue_diamond': '🔹',
    'small_orange_diamond': '🔸', 'smiling_cat_face_with_heart-eyes': '😻',
    'smiling_face': '☺', 'smiling_face_with_halo': '😇',
    'smiling_face_with_3_hearts': '🥰', 'smiling_face_with_heart-eyes': '😍',
    'smiling_face_with_horns': '😈', 'smiling_face_with_smiling_eyes': '😊',
    'smiling_face_with_sunglasses': '😎', 'smirking_face': '😏', 'snail': '🐌',
    'snake': '🐍', 'sneezing_face': '🤧', 'snow-capped_mountain': '🏔',
    'snowboarder': '🏂', 'snowboarder_dark_skin_tone': '🏂🏿',
    'snowboarder_light_skin_tone': '🏂🏻',
    'snowboarder_medium-dark_skin_tone': '🏂🏾',
    'snowboarder_medium-light_skin_tone': '🏂🏼',
    'snowboarder_medium_skin_tone': '🏂🏽', 'snowflake': '❄', 'snowman': '☃',
    'snowman_without_snow': '⛄', 'soap': '🧼', 'soccer_ball': '⚽', 'socks':
    '🧦', 'softball': '🥎', 'soft_ice_cream': '🍦', 'spade_suit': '♠',
    'spaghetti': '🍝', 'sparkle': '❇', 'sparkler': '🎇', 'sparkles': '✨',
    'sparkling_heart': '💖', 'speak-no-evil_monkey': '🙊',
    'speaker_high_volume': '🔊', 'speaker_low_volume': '🔈',
    'speaker_medium_volume': '🔉', 'speaking_head': '🗣', 'speech_balloon':
    '💬', 'speedboat': '🚤', 'spider': '🕷', 'spider_web': '🕸',
    'spiral_calendar': '🗓', 'spiral_notepad': '🗒', 'spiral_shell': '🐚',
    'spoon': '🥄', 'sponge': '🧽', 'sport_utility_vehicle': '🚙',
    'sports_medal': '🏅', 'spouting_whale': '🐳', 'squid': '🦑',
    'squinting_face_with_tongue': '😝', 'stadium': '🏟', 'star-struck': '🤩',
    'star_and_crescent': '☪', 'star_of_david': '✡', 'station': '🚉',
    'steaming_bowl': '🍜', 'stethoscope': '🩺', 'stop_button': '⏹',
    'stop_sign': '🛑', 'stopwatch': '⏱', 'straight_ruler': '📏', 'strawberry':
    '🍓', 'studio_microphone': '🎙', 'stuffed_flatbread': '🥙', 'sun': '☀',
    'sun_behind_cloud': '⛅', 'sun_behind_large_cloud': '🌥',
    'sun_behind_rain_cloud': '🌦', 'sun_behind_small_cloud': '🌤',
    'sun_with_face': '🌞', 'sunflower': '🌻', 'sunglasses': '😎', 'sunrise':
    '🌅', 'sunrise_over_mountains': '🌄', 'sunset': '🌇', 'superhero': '🦸',
    'supervillain': '🦹', 'sushi': '🍣', 'suspension_railway': '🚟', 'swan':
    '🦢', 'sweat_droplets': '💦', 'synagogue': '🕍', 'syringe': '💉', 't-shirt':
    '👕', 'taco': '🌮', 'takeout_box': '🥡', 'tanabata_tree': '🎋', 'tangerine':
    '🍊', 'taxi': '🚕', 'teacup_without_handle': '🍵', 'tear-off_calendar':
    '📆', 'teddy_bear': '🧸', 'telephone': '☎', 'telephone_receiver': '📞',
    'telescope': '🔭', 'television': '📺', 'ten-thirty': '🕥', 'ten_o’clock':
    '🕙', 'tennis': '🎾', 'tent': '⛺', 'test_tube': '🧪', 'thermometer': '🌡',
    'thinking_face': '🤔', 'thought_balloon': '💭', 'thread': '🧵',
    'three-thirty': '🕞', 'three_o’clock': '🕒', 'thumbs_down': '👎',
    'thumbs_down_dark_skin_tone': '👎🏿', 'thumbs_down_light_skin_tone': '👎🏻',
    'thumbs_down_medium-dark_skin_tone': '👎🏾',
    'thumbs_down_medium-light_skin_tone': '👎🏼',
    'thumbs_down_medium_skin_tone': '👎🏽', 'thumbs_up': '👍',
    'thumbs_up_dark_skin_tone': '👍🏿', 'thumbs_up_light_skin_tone': '👍🏻',
    'thumbs_up_medium-dark_skin_tone': '👍🏾',
    'thumbs_up_medium-light_skin_tone': '👍🏼', 'thumbs_up_medium_skin_tone':
    '👍🏽', 'ticket': '🎫', 'tiger': '🐯', 'tiger_face': '🐯', 'timer_clock':
    '⏲', 'tired_face': '😫', 'toolbox': '🧰', 'toilet': '🚽', 'tomato': '🍅',
    'tongue': '👅', 'tooth': '🦷', 'top_hat': '🎩', 'tornado': '🌪',
    'trackball': '🖲', 'tractor': '🚜', 'trade_mark': '™', 'train': '🚋',
    'tram': '🚊', 'tram_car': '🚋', 'triangular_flag': '🚩',
    'triangular_ruler': '📐', 'trident_emblem': '🔱', 'trolleybus': '🚎',
    'trophy': '🏆', 'tropical_drink': '🍹', 'tropical_fish': '🐠', 'trumpet':
    '🎺', 'tulip': '🌷', 'tumbler_glass': '🥃', 'turtle': '🐢', 'twelve-thirty':
    '🕧', 'twelve_o’clock': '🕛', 'two-hump_camel': '🐫', 'two-thirty': '🕝',
    'two_hearts': '💕', 'two_men_holding_hands': '👬', 'two_o’clock': '🕑',
    'two_women_holding_hands': '👭', 'umbrella': '☂', 'umbrella_on_ground':
    '⛱', 'umbrella_with_rain_drops': '☔', 'unamused_face': '😒',
    'unicorn_face': '🦄', 'unlocked': '🔓', 'up-down_arrow': '↕',
    'up-left_arrow': '↖', 'up-right_arrow': '↗', 'up_arrow': '⬆',
    'upside-down_face': '🙃', 'upwards_button': '🔼', 'vampire': '🧛',
    'vampire_dark_skin_tone': '🧛🏿', 'vampire_light_skin_tone': '🧛🏻',
    'vampire_medium-dark_skin_tone': '🧛🏾', 'vampire_medium-light_skin_tone':
    '🧛🏼', 'vampire_medium_skin_tone': '🧛🏽', 'vertical_traffic_light': '🚦',
    'vibration_mode': '📳', 'victory_hand': '✌',
    'victory_hand_dark_skin_tone': '✌🏿', 'victory_hand_light_skin_tone':
    '✌🏻', 'victory_hand_medium-dark_skin_tone': '✌🏾',
    'victory_hand_medium-light_skin_tone': '✌🏼',
    'victory_hand_medium_skin_tone': '✌🏽', 'video_camera': '📹',
    'video_game': '🎮', 'videocassette': '📼', 'violin': '🎻', 'volcano': '🌋',
    'volleyball': '🏐', 'vulcan_salute': '🖖', 'vulcan_salute_dark_skin_tone':
    '🖖🏿', 'vulcan_salute_light_skin_tone': '🖖🏻',
    'vulcan_salute_medium-dark_skin_tone': '🖖🏾',
    'vulcan_salute_medium-light_skin_tone': '🖖🏼',
    'vulcan_salute_medium_skin_tone': '🖖🏽', 'waffle': '🧇',
    'waning_crescent_moon': '🌘', 'waning_gibbous_moon': '🌖', 'warning': '⚠',
    'wastebasket': '🗑', 'watch': '⌚', 'water_buffalo': '🐃', 'water_closet':
    '🚾', 'water_wave': '🌊', 'watermelon': '🍉', 'waving_hand': '👋',
    'waving_hand_dark_skin_tone': '👋🏿', 'waving_hand_light_skin_tone': '👋🏻',
    'waving_hand_medium-dark_skin_tone': '👋🏾',
    'waving_hand_medium-light_skin_tone': '👋🏼',
    'waving_hand_medium_skin_tone': '👋🏽', 'wavy_dash': '〰',
    'waxing_crescent_moon': '🌒', 'waxing_gibbous_moon': '🌔',
    'weary_cat_face': '🙀', 'weary_face': '😩', 'wedding': '💒', 'whale': '🐳',
    'wheel_of_dharma': '☸', 'wheelchair_symbol': '♿', 'white_circle': '⚪',
    'white_exclamation_mark': '❕', 'white_flag': '🏳', 'white_flower': '💮',
    'white_hair': '🦳', 'white-haired_man': '👨\u200d🦳', 'white-haired_woman':
    '👩\u200d🦳', 'white_heart': '🤍', 'white_heavy_check_mark': '✅',
    'white_large_square': '⬜', 'white_medium-small_square': '◽',
    'white_medium_square': '◻', 'white_medium_star': '⭐',
    'white_question_mark': '❔', 'white_small_square': '▫',
    'white_square_button': '🔳', 'wilted_flower': '🥀', 'wind_chime': '🎐',
    'wind_face': '🌬', 'wine_glass': '🍷', 'winking_face': '😉',
    'winking_face_with_tongue': '😜', 'wolf_face': '🐺', 'woman': '👩',
    'woman_artist': '👩\u200d🎨', 'woman_artist_dark_skin_tone': '👩🏿\u200d🎨',
    'woman_artist_light_skin_tone': '👩🏻\u200d🎨',
    'woman_artist_medium-dark_skin_tone': '👩🏾\u200d🎨',
    'woman_artist_medium-light_skin_tone': '👩🏼\u200d🎨',
    'woman_artist_medium_skin_tone': '👩🏽\u200d🎨', 'woman_astronaut':
    '👩\u200d🚀', 'woman_astronaut_dark_skin_tone': '👩🏿\u200d🚀',
    'woman_astronaut_light_skin_tone': '👩🏻\u200d🚀',
    'woman_astronaut_medium-dark_skin_tone': '👩🏾\u200d🚀',
    'woman_astronaut_medium-light_skin_tone': '👩🏼\u200d🚀',
    'woman_astronaut_medium_skin_tone': '👩🏽\u200d🚀', 'woman_biking':
    '🚴\u200d♀️', 'woman_biking_dark_skin_tone': '🚴🏿\u200d♀️',
    'woman_biking_light_skin_tone': '🚴🏻\u200d♀️',
    'woman_biking_medium-dark_skin_tone': '🚴🏾\u200d♀️',
    'woman_biking_medium-light_skin_tone': '🚴🏼\u200d♀️',
    'woman_biking_medium_skin_tone': '🚴🏽\u200d♀️', 'woman_bouncing_ball':
    '⛹️\u200d♀️', 'woman_bouncing_ball_dark_skin_tone': '⛹🏿\u200d♀️',
    'woman_bouncing_ball_light_skin_tone': '⛹🏻\u200d♀️',
    'woman_bouncing_ball_medium-dark_skin_tone': '⛹🏾\u200d♀️',
    'woman_bouncing_ball_medium-light_skin_tone': '⛹🏼\u200d♀️',
    'woman_bouncing_ball_medium_skin_tone': '⛹🏽\u200d♀️', 'woman_bowing':
    '🙇\u200d♀️', 'woman_bowing_dark_skin_tone': '🙇🏿\u200d♀️',
    'woman_bowing_light_skin_tone': '🙇🏻\u200d♀️',
    'woman_bowing_medium-dark_skin_tone': '🙇🏾\u200d♀️',
    'woman_bowing_medium-light_skin_tone': '🙇🏼\u200d♀️',
    'woman_bowing_medium_skin_tone': '🙇🏽\u200d♀️', 'woman_cartwheeling':
    '🤸\u200d♀️', 'woman_cartwheeling_dark_skin_tone': '🤸🏿\u200d♀️',
    'woman_cartwheeling_light_skin_tone': '🤸🏻\u200d♀️',
    'woman_cartwheeling_medium-dark_skin_tone': '🤸🏾\u200d♀️',
    'woman_cartwheeling_medium-light_skin_tone': '🤸🏼\u200d♀️',
    'woman_cartwheeling_medium_skin_tone': '🤸🏽\u200d♀️', 'woman_climbing':
    '🧗\u200d♀️', 'woman_climbing_dark_skin_tone': '🧗🏿\u200d♀️',
    'woman_climbing_light_skin_tone': '🧗🏻\u200d♀️',
    'woman_climbing_medium-dark_skin_tone': '🧗🏾\u200d♀️',
    'woman_climbing_medium-light_skin_tone': '🧗🏼\u200d♀️',
    'woman_climbing_medium_skin_tone': '🧗🏽\u200d♀️',
    'woman_construction_worker': '👷\u200d♀️',
    'woman_construction_worker_dark_skin_tone': '👷🏿\u200d♀️',
    'woman_construction_worker_light_skin_tone': '👷🏻\u200d♀️',
    'woman_construction_worker_medium-dark_skin_tone': '👷🏾\u200d♀️',
    'woman_construction_worker_medium-light_skin_tone': '👷🏼\u200d♀️',
    'woman_construction_worker_medium_skin_tone': '👷🏽\u200d♀️',
    'woman_cook': '👩\u200d🍳', 'woman_cook_dark_skin_tone': '👩🏿\u200d🍳',
    'woman_cook_light_skin_tone': '👩🏻\u200d🍳',
    'woman_cook_medium-dark_skin_tone': '👩🏾\u200d🍳',
    'woman_cook_medium-light_skin_tone': '👩🏼\u200d🍳',
    'woman_cook_medium_skin_tone': '👩🏽\u200d🍳', 'woman_dancing': '💃',
    'woman_dancing_dark_skin_tone': '💃🏿', 'woman_dancing_light_skin_tone':
    '💃🏻', 'woman_dancing_medium-dark_skin_tone': '💃🏾',
    'woman_dancing_medium-light_skin_tone': '💃🏼',
    'woman_dancing_medium_skin_tone': '💃🏽', 'woman_dark_skin_tone': '👩🏿',
    'woman_detective': '🕵️\u200d♀️', 'woman_detective_dark_skin_tone':
    '🕵🏿\u200d♀️', 'woman_detective_light_skin_tone': '🕵🏻\u200d♀️',
    'woman_detective_medium-dark_skin_tone': '🕵🏾\u200d♀️',
    'woman_detective_medium-light_skin_tone': '🕵🏼\u200d♀️',
    'woman_detective_medium_skin_tone': '🕵🏽\u200d♀️', 'woman_elf':
    '🧝\u200d♀️', 'woman_elf_dark_skin_tone': '🧝🏿\u200d♀️',
    'woman_elf_light_skin_tone': '🧝🏻\u200d♀️',
    'woman_elf_medium-dark_skin_tone': '🧝🏾\u200d♀️',
    'woman_elf_medium-light_skin_tone': '🧝🏼\u200d♀️',
    'woman_elf_medium_skin_tone': '🧝🏽\u200d♀️', 'woman_facepalming':
    '🤦\u200d♀️', 'woman_facepalming_dark_skin_tone': '🤦🏿\u200d♀️',
    'woman_facepalming_light_skin_tone': '🤦🏻\u200d♀️',
    'woman_facepalming_medium-dark_skin_tone': '🤦🏾\u200d♀️',
    'woman_facepalming_medium-light_skin_tone': '🤦🏼\u200d♀️',
    'woman_facepalming_medium_skin_tone': '🤦🏽\u200d♀️',
    'woman_factory_worker': '👩\u200d🏭',
    'woman_factory_worker_dark_skin_tone': '👩🏿\u200d🏭',
    'woman_factory_worker_light_skin_tone': '👩🏻\u200d🏭',
    'woman_factory_worker_medium-dark_skin_tone': '👩🏾\u200d🏭',
    'woman_factory_worker_medium-light_skin_tone': '👩🏼\u200d🏭',
    'woman_factory_worker_medium_skin_tone': '👩🏽\u200d🏭', 'woman_fairy':
    '🧚\u200d♀️', 'woman_fairy_dark_skin_tone': '🧚🏿\u200d♀️',
    'woman_fairy_light_skin_tone': '🧚🏻\u200d♀️',
    'woman_fairy_medium-dark_skin_tone': '🧚🏾\u200d♀️',
    'woman_fairy_medium-light_skin_tone': '🧚🏼\u200d♀️',
    'woman_fairy_medium_skin_tone': '🧚🏽\u200d♀️', 'woman_farmer':
    '👩\u200d🌾', 'woman_farmer_dark_skin_tone': '👩🏿\u200d🌾',
    'woman_farmer_light_skin_tone': '👩🏻\u200d🌾',
    'woman_farmer_medium-dark_skin_tone': '👩🏾\u200d🌾',
    'woman_farmer_medium-light_skin_tone': '👩🏼\u200d🌾',
    'woman_farmer_medium_skin_tone': '👩🏽\u200d🌾', 'woman_firefighter':
    '👩\u200d🚒', 'woman_firefighter_dark_skin_tone': '👩🏿\u200d🚒',
    'woman_firefighter_light_skin_tone': '👩🏻\u200d🚒',
    'woman_firefighter_medium-dark_skin_tone': '👩🏾\u200d🚒',
    'woman_firefighter_medium-light_skin_tone': '👩🏼\u200d🚒',
    'woman_firefighter_medium_skin_tone': '👩🏽\u200d🚒', 'woman_frowning':
    '🙍\u200d♀️', 'woman_frowning_dark_skin_tone': '🙍🏿\u200d♀️',
    'woman_frowning_light_skin_tone': '🙍🏻\u200d♀️',
    'woman_frowning_medium-dark_skin_tone': '🙍🏾\u200d♀️',
    'woman_frowning_medium-light_skin_tone': '🙍🏼\u200d♀️',
    'woman_frowning_medium_skin_tone': '🙍🏽\u200d♀️', 'woman_genie':
    '🧞\u200d♀️', 'woman_gesturing_no': '🙅\u200d♀️',
    'woman_gesturing_no_dark_skin_tone': '🙅🏿\u200d♀️',
    'woman_gesturing_no_light_skin_tone': '🙅🏻\u200d♀️',
    'woman_gesturing_no_medium-dark_skin_tone': '🙅🏾\u200d♀️',
    'woman_gesturing_no_medium-light_skin_tone': '🙅🏼\u200d♀️',
    'woman_gesturing_no_medium_skin_tone': '🙅🏽\u200d♀️',
    'woman_gesturing_ok': '🙆\u200d♀️', 'woman_gesturing_ok_dark_skin_tone':
    '🙆🏿\u200d♀️', 'woman_gesturing_ok_light_skin_tone': '🙆🏻\u200d♀️',
    'woman_gesturing_ok_medium-dark_skin_tone': '🙆🏾\u200d♀️',
    'woman_gesturing_ok_medium-light_skin_tone': '🙆🏼\u200d♀️',
    'woman_gesturing_ok_medium_skin_tone': '🙆🏽\u200d♀️',
    'woman_getting_haircut': '💇\u200d♀️',
    'woman_getting_haircut_dark_skin_tone': '💇🏿\u200d♀️',
    'woman_getting_haircut_light_skin_tone': '💇🏻\u200d♀️',
    'woman_getting_haircut_medium-dark_skin_tone': '💇🏾\u200d♀️',
    'woman_getting_haircut_medium-light_skin_tone': '💇🏼\u200d♀️',
    'woman_getting_haircut_medium_skin_tone': '💇🏽\u200d♀️',
    'woman_getting_massage': '💆\u200d♀️',
    'woman_getting_massage_dark_skin_tone': '💆🏿\u200d♀️',
    'woman_getting_massage_light_skin_tone': '💆🏻\u200d♀️',
    'woman_getting_massage_medium-dark_skin_tone': '💆🏾\u200d♀️',
    'woman_getting_massage_medium-light_skin_tone': '💆🏼\u200d♀️',
    'woman_getting_massage_medium_skin_tone': '💆🏽\u200d♀️', 'woman_golfing':
    '🏌️\u200d♀️', 'woman_golfing_dark_skin_tone': '🏌🏿\u200d♀️',
    'woman_golfing_light_skin_tone': '🏌🏻\u200d♀️',
    'woman_golfing_medium-dark_skin_tone': '🏌🏾\u200d♀️',
    'woman_golfing_medium-light_skin_tone': '🏌🏼\u200d♀️',
    'woman_golfing_medium_skin_tone': '🏌🏽\u200d♀️', 'woman_guard':
    '💂\u200d♀️', 'woman_guard_dark_skin_tone': '💂🏿\u200d♀️',
    'woman_guard_light_skin_tone': '💂🏻\u200d♀️',
    'woman_guard_medium-dark_skin_tone': '💂🏾\u200d♀️',
    'woman_guard_medium-light_skin_tone': '💂🏼\u200d♀️',
    'woman_guard_medium_skin_tone': '💂🏽\u200d♀️', 'woman_health_worker':
    '👩\u200d⚕️', 'woman_health_worker_dark_skin_tone': '👩🏿\u200d⚕️',
    'woman_health_worker_light_skin_tone': '👩🏻\u200d⚕️',
    'woman_health_worker_medium-dark_skin_tone': '👩🏾\u200d⚕️',
    'woman_health_worker_medium-light_skin_tone': '👩🏼\u200d⚕️',
    'woman_health_worker_medium_skin_tone': '👩🏽\u200d⚕️',
    'woman_in_lotus_position': '🧘\u200d♀️',
    'woman_in_lotus_position_dark_skin_tone': '🧘🏿\u200d♀️',
    'woman_in_lotus_position_light_skin_tone': '🧘🏻\u200d♀️',
    'woman_in_lotus_position_medium-dark_skin_tone': '🧘🏾\u200d♀️',
    'woman_in_lotus_position_medium-light_skin_tone': '🧘🏼\u200d♀️',
    'woman_in_lotus_position_medium_skin_tone': '🧘🏽\u200d♀️',
    'woman_in_manual_wheelchair': '👩\u200d🦽',
    'woman_in_motorized_wheelchair': '👩\u200d🦼', 'woman_in_steamy_room':
    '🧖\u200d♀️', 'woman_in_steamy_room_dark_skin_tone': '🧖🏿\u200d♀️',
    'woman_in_steamy_room_light_skin_tone': '🧖🏻\u200d♀️',
    'woman_in_steamy_room_medium-dark_skin_tone': '🧖🏾\u200d♀️',
    'woman_in_steamy_room_medium-light_skin_tone': '🧖🏼\u200d♀️',
    'woman_in_steamy_room_medium_skin_tone': '🧖🏽\u200d♀️', 'woman_judge':
    '👩\u200d⚖️', 'woman_judge_dark_skin_tone': '👩🏿\u200d⚖️',
    'woman_judge_light_skin_tone': '👩🏻\u200d⚖️',
    'woman_judge_medium-dark_skin_tone': '👩🏾\u200d⚖️',
    'woman_judge_medium-light_skin_tone': '👩🏼\u200d⚖️',
    'woman_judge_medium_skin_tone': '👩🏽\u200d⚖️', 'woman_juggling':
    '🤹\u200d♀️', 'woman_juggling_dark_skin_tone': '🤹🏿\u200d♀️',
    'woman_juggling_light_skin_tone': '🤹🏻\u200d♀️',
    'woman_juggling_medium-dark_skin_tone': '🤹🏾\u200d♀️',
    'woman_juggling_medium-light_skin_tone': '🤹🏼\u200d♀️',
    'woman_juggling_medium_skin_tone': '🤹🏽\u200d♀️',
    'woman_lifting_weights': '🏋️\u200d♀️',
    'woman_lifting_weights_dark_skin_tone': '🏋🏿\u200d♀️',
    'woman_lifting_weights_light_skin_tone': '🏋🏻\u200d♀️',
    'woman_lifting_weights_medium-dark_skin_tone': '🏋🏾\u200d♀️',
    'woman_lifting_weights_medium-light_skin_tone': '🏋🏼\u200d♀️',
    'woman_lifting_weights_medium_skin_tone': '🏋🏽\u200d♀️',
    'woman_light_skin_tone': '👩🏻', 'woman_mage': '🧙\u200d♀️',
    'woman_mage_dark_skin_tone': '🧙🏿\u200d♀️', 'woman_mage_light_skin_tone':
    '🧙🏻\u200d♀️', 'woman_mage_medium-dark_skin_tone': '🧙🏾\u200d♀️',
    'woman_mage_medium-light_skin_tone': '🧙🏼\u200d♀️',
    'woman_mage_medium_skin_tone': '🧙🏽\u200d♀️', 'woman_mechanic':
    '👩\u200d🔧', 'woman_mechanic_dark_skin_tone': '👩🏿\u200d🔧',
    'woman_mechanic_light_skin_tone': '👩🏻\u200d🔧',
    'woman_mechanic_medium-dark_skin_tone': '👩🏾\u200d🔧',
    'woman_mechanic_medium-light_skin_tone': '👩🏼\u200d🔧',
    'woman_mechanic_medium_skin_tone': '👩🏽\u200d🔧',
    'woman_medium-dark_skin_tone': '👩🏾', 'woman_medium-light_skin_tone':
    '👩🏼', 'woman_medium_skin_tone': '👩🏽', 'woman_mountain_biking':
    '🚵\u200d♀️', 'woman_mountain_biking_dark_skin_tone': '🚵🏿\u200d♀️',
    'woman_mountain_biking_light_skin_tone': '🚵🏻\u200d♀️',
    'woman_mountain_biking_medium-dark_skin_tone': '🚵🏾\u200d♀️',
    'woman_mountain_biking_medium-light_skin_tone': '🚵🏼\u200d♀️',
    'woman_mountain_biking_medium_skin_tone': '🚵🏽\u200d♀️',
    'woman_office_worker': '👩\u200d💼', 'woman_office_worker_dark_skin_tone':
    '👩🏿\u200d💼', 'woman_office_worker_light_skin_tone': '👩🏻\u200d💼',
    'woman_office_worker_medium-dark_skin_tone': '👩🏾\u200d💼',
    'woman_office_worker_medium-light_skin_tone': '👩🏼\u200d💼',
    'woman_office_worker_medium_skin_tone': '👩🏽\u200d💼', 'woman_pilot':
    '👩\u200d✈️', 'woman_pilot_dark_skin_tone': '👩🏿\u200d✈️',
    'woman_pilot_light_skin_tone': '👩🏻\u200d✈️',
    'woman_pilot_medium-dark_skin_tone': '👩🏾\u200d✈️',
    'woman_pilot_medium-light_skin_tone': '👩🏼\u200d✈️',
    'woman_pilot_medium_skin_tone': '👩🏽\u200d✈️', 'woman_playing_handball':
    '🤾\u200d♀️', 'woman_playing_handball_dark_skin_tone': '🤾🏿\u200d♀️',
    'woman_playing_handball_light_skin_tone': '🤾🏻\u200d♀️',
    'woman_playing_handball_medium-dark_skin_tone': '🤾🏾\u200d♀️',
    'woman_playing_handball_medium-light_skin_tone': '🤾🏼\u200d♀️',
    'woman_playing_handball_medium_skin_tone': '🤾🏽\u200d♀️',
    'woman_playing_water_polo': '🤽\u200d♀️',
    'woman_playing_water_polo_dark_skin_tone': '🤽🏿\u200d♀️',
    'woman_playing_water_polo_light_skin_tone': '🤽🏻\u200d♀️',
    'woman_playing_water_polo_medium-dark_skin_tone': '🤽🏾\u200d♀️',
    'woman_playing_water_polo_medium-light_skin_tone': '🤽🏼\u200d♀️',
    'woman_playing_water_polo_medium_skin_tone': '🤽🏽\u200d♀️',
    'woman_police_officer': '👮\u200d♀️',
    'woman_police_officer_dark_skin_tone': '👮🏿\u200d♀️',
    'woman_police_officer_light_skin_tone': '👮🏻\u200d♀️',
    'woman_police_officer_medium-dark_skin_tone': '👮🏾\u200d♀️',
    'woman_police_officer_medium-light_skin_tone': '👮🏼\u200d♀️',
    'woman_police_officer_medium_skin_tone': '👮🏽\u200d♀️', 'woman_pouting':
    '🙎\u200d♀️', 'woman_pouting_dark_skin_tone': '🙎🏿\u200d♀️',
    'woman_pouting_light_skin_tone': '🙎🏻\u200d♀️',
    'woman_pouting_medium-dark_skin_tone': '🙎🏾\u200d♀️',
    'woman_pouting_medium-light_skin_tone': '🙎🏼\u200d♀️',
    'woman_pouting_medium_skin_tone': '🙎🏽\u200d♀️', 'woman_raising_hand':
    '🙋\u200d♀️', 'woman_raising_hand_dark_skin_tone': '🙋🏿\u200d♀️',
    'woman_raising_hand_light_skin_tone': '🙋🏻\u200d♀️',
    'woman_raising_hand_medium-dark_skin_tone': '🙋🏾\u200d♀️',
    'woman_raising_hand_medium-light_skin_tone': '🙋🏼\u200d♀️',
    'woman_raising_hand_medium_skin_tone': '🙋🏽\u200d♀️',
    'woman_rowing_boat': '🚣\u200d♀️', 'woman_rowing_boat_dark_skin_tone':
    '🚣🏿\u200d♀️', 'woman_rowing_boat_light_skin_tone': '🚣🏻\u200d♀️',
    'woman_rowing_boat_medium-dark_skin_tone': '🚣🏾\u200d♀️',
    'woman_rowing_boat_medium-light_skin_tone': '🚣🏼\u200d♀️',
    'woman_rowing_boat_medium_skin_tone': '🚣🏽\u200d♀️', 'woman_running':
    '🏃\u200d♀️', 'woman_running_dark_skin_tone': '🏃🏿\u200d♀️',
    'woman_running_light_skin_tone': '🏃🏻\u200d♀️',
    'woman_running_medium-dark_skin_tone': '🏃🏾\u200d♀️',
    'woman_running_medium-light_skin_tone': '🏃🏼\u200d♀️',
    'woman_running_medium_skin_tone': '🏃🏽\u200d♀️', 'woman_scientist':
    '👩\u200d🔬', 'woman_scientist_dark_skin_tone': '👩🏿\u200d🔬',
    'woman_scientist_light_skin_tone': '👩🏻\u200d🔬',
    'woman_scientist_medium-dark_skin_tone': '👩🏾\u200d🔬',
    'woman_scientist_medium-light_skin_tone': '👩🏼\u200d🔬',
    'woman_scientist_medium_skin_tone': '👩🏽\u200d🔬', 'woman_shrugging':
    '🤷\u200d♀️', 'woman_shrugging_dark_skin_tone': '🤷🏿\u200d♀️',
    'woman_shrugging_light_skin_tone': '🤷🏻\u200d♀️',
    'woman_shrugging_medium-dark_skin_tone': '🤷🏾\u200d♀️',
    'woman_shrugging_medium-light_skin_tone': '🤷🏼\u200d♀️',
    'woman_shrugging_medium_skin_tone': '🤷🏽\u200d♀️', 'woman_singer':
    '👩\u200d🎤', 'woman_singer_dark_skin_tone': '👩🏿\u200d🎤',
    'woman_singer_light_skin_tone': '👩🏻\u200d🎤',
    'woman_singer_medium-dark_skin_tone': '👩🏾\u200d🎤',
    'woman_singer_medium-light_skin_tone': '👩🏼\u200d🎤',
    'woman_singer_medium_skin_tone': '👩🏽\u200d🎤', 'woman_student':
    '👩\u200d🎓', 'woman_student_dark_skin_tone': '👩🏿\u200d🎓',
    'woman_student_light_skin_tone': '👩🏻\u200d🎓',
    'woman_student_medium-dark_skin_tone': '👩🏾\u200d🎓',
    'woman_student_medium-light_skin_tone': '👩🏼\u200d🎓',
    'woman_student_medium_skin_tone': '👩🏽\u200d🎓', 'woman_surfing':
    '🏄\u200d♀️', 'woman_surfing_dark_skin_tone': '🏄🏿\u200d♀️',
    'woman_surfing_light_skin_tone': '🏄🏻\u200d♀️',
    'woman_surfing_medium-dark_skin_tone': '🏄🏾\u200d♀️',
    'woman_surfing_medium-light_skin_tone': '🏄🏼\u200d♀️',
    'woman_surfing_medium_skin_tone': '🏄🏽\u200d♀️', 'woman_swimming':
    '🏊\u200d♀️', 'woman_swimming_dark_skin_tone': '🏊🏿\u200d♀️',
    'woman_swimming_light_skin_tone': '🏊🏻\u200d♀️',
    'woman_swimming_medium-dark_skin_tone': '🏊🏾\u200d♀️',
    'woman_swimming_medium-light_skin_tone': '🏊🏼\u200d♀️',
    'woman_swimming_medium_skin_tone': '🏊🏽\u200d♀️', 'woman_teacher':
    '👩\u200d🏫', 'woman_teacher_dark_skin_tone': '👩🏿\u200d🏫',
    'woman_teacher_light_skin_tone': '👩🏻\u200d🏫',
    'woman_teacher_medium-dark_skin_tone': '👩🏾\u200d🏫',
    'woman_teacher_medium-light_skin_tone': '👩🏼\u200d🏫',
    'woman_teacher_medium_skin_tone': '👩🏽\u200d🏫', 'woman_technologist':
    '👩\u200d💻', 'woman_technologist_dark_skin_tone': '👩🏿\u200d💻',
    'woman_technologist_light_skin_tone': '👩🏻\u200d💻',
    'woman_technologist_medium-dark_skin_tone': '👩🏾\u200d💻',
    'woman_technologist_medium-light_skin_tone': '👩🏼\u200d💻',
    'woman_technologist_medium_skin_tone': '👩🏽\u200d💻',
    'woman_tipping_hand': '💁\u200d♀️', 'woman_tipping_hand_dark_skin_tone':
    '💁🏿\u200d♀️', 'woman_tipping_hand_light_skin_tone': '💁🏻\u200d♀️',
    'woman_tipping_hand_medium-dark_skin_tone': '💁🏾\u200d♀️',
    'woman_tipping_hand_medium-light_skin_tone': '💁🏼\u200d♀️',
    'woman_tipping_hand_medium_skin_tone': '💁🏽\u200d♀️', 'woman_vampire':
    '🧛\u200d♀️', 'woman_vampire_dark_skin_tone': '🧛🏿\u200d♀️',
    'woman_vampire_light_skin_tone': '🧛🏻\u200d♀️',
    'woman_vampire_medium-dark_skin_tone': '🧛🏾\u200d♀️',
    'woman_vampire_medium-light_skin_tone': '🧛🏼\u200d♀️',
    'woman_vampire_medium_skin_tone': '🧛🏽\u200d♀️', 'woman_walking':
    '🚶\u200d♀️', 'woman_walking_dark_skin_tone': '🚶🏿\u200d♀️',
    'woman_walking_light_skin_tone': '🚶🏻\u200d♀️',
    'woman_walking_medium-dark_skin_tone': '🚶🏾\u200d♀️',
    'woman_walking_medium-light_skin_tone': '🚶🏼\u200d♀️',
    'woman_walking_medium_skin_tone': '🚶🏽\u200d♀️', 'woman_wearing_turban':
    '👳\u200d♀️', 'woman_wearing_turban_dark_skin_tone': '👳🏿\u200d♀️',
    'woman_wearing_turban_light_skin_tone': '👳🏻\u200d♀️',
    'woman_wearing_turban_medium-dark_skin_tone': '👳🏾\u200d♀️',
    'woman_wearing_turban_medium-light_skin_tone': '👳🏼\u200d♀️',
    'woman_wearing_turban_medium_skin_tone': '👳🏽\u200d♀️',
    'woman_with_headscarf': '🧕', 'woman_with_headscarf_dark_skin_tone':
    '🧕🏿', 'woman_with_headscarf_light_skin_tone': '🧕🏻',
    'woman_with_headscarf_medium-dark_skin_tone': '🧕🏾',
    'woman_with_headscarf_medium-light_skin_tone': '🧕🏼',
    'woman_with_headscarf_medium_skin_tone': '🧕🏽',
    'woman_with_probing_cane': '👩\u200d🦯', 'woman_zombie': '🧟\u200d♀️',
    'woman’s_boot': '👢', 'woman’s_clothes': '👚', 'woman’s_hat': '👒',
    'woman’s_sandal': '👡', 'women_with_bunny_ears': '👯\u200d♀️',
    'women_wrestling': '🤼\u200d♀️', 'women’s_room': '🚺', 'woozy_face': '🥴',
    'world_map': '🗺', 'worried_face': '😟', 'wrapped_gift': '🎁', 'wrench':
    '🔧', 'writing_hand': '✍', 'writing_hand_dark_skin_tone': '✍🏿',
    'writing_hand_light_skin_tone': '✍🏻',
    'writing_hand_medium-dark_skin_tone': '✍🏾',
    'writing_hand_medium-light_skin_tone': '✍🏼',
    'writing_hand_medium_skin_tone': '✍🏽', 'yarn': '🧶', 'yawning_face': '🥱',
    'yellow_circle': '🟡', 'yellow_heart': '💛', 'yellow_square': '🟨',
    'yen_banknote': '💴', 'yo-yo': '🪀', 'yin_yang': '☯', 'zany_face': '🤪',
    'zebra': '🦓', 'zipper-mouth_face': '🤐', 'zombie': '🧟', 'zzz': '💤',
    'åland_islands': '🇦🇽', 'keycap_asterisk': '*⃣', 'keycap_digit_eight':
    '8⃣', 'keycap_digit_five': '5⃣', 'keycap_digit_four': '4⃣',
    'keycap_digit_nine': '9⃣', 'keycap_digit_one': '1⃣',
    'keycap_digit_seven': '7⃣', 'keycap_digit_six': '6⃣',
    'keycap_digit_three': '3⃣', 'keycap_digit_two': '2⃣',
    'keycap_digit_zero': '0⃣', 'keycap_number_sign': '#⃣',
    'light_skin_tone': '🏻', 'medium_light_skin_tone': '🏼',
    'medium_skin_tone': '🏽', 'medium_dark_skin_tone': '🏾', 'dark_skin_tone':
    '🏿', 'regional_indicator_symbol_letter_a': '🇦',
    'regional_indicator_symbol_letter_b': '🇧',
    'regional_indicator_symbol_letter_c': '🇨',
    'regional_indicator_symbol_letter_d': '🇩',
    'regional_indicator_symbol_letter_e': '🇪',
    'regional_indicator_symbol_letter_f': '🇫',
    'regional_indicator_symbol_letter_g': '🇬',
    'regional_indicator_symbol_letter_h': '🇭',
    'regional_indicator_symbol_letter_i': '🇮',
    'regional_indicator_symbol_letter_j': '🇯',
    'regional_indicator_symbol_letter_k': '🇰',
    'regional_indicator_symbol_letter_l': '🇱',
    'regional_indicator_symbol_letter_m': '🇲',
    'regional_indicator_symbol_letter_n': '🇳',
    'regional_indicator_symbol_letter_o': '🇴',
    'regional_indicator_symbol_letter_p': '🇵',
    'regional_indicator_symbol_letter_q': '🇶',
    'regional_indicator_symbol_letter_r': '🇷',
    'regional_indicator_symbol_letter_s': '🇸',
    'regional_indicator_symbol_letter_t': '🇹',
    'regional_indicator_symbol_letter_u': '🇺',
    'regional_indicator_symbol_letter_v': '🇻',
    'regional_indicator_symbol_letter_w': '🇼',
    'regional_indicator_symbol_letter_x': '🇽',
    'regional_indicator_symbol_letter_y': '🇾',
    'regional_indicator_symbol_letter_z': '🇿', 'airplane_arriving': '🛬',
    'space_invader': '👾', 'football': '🏈', 'anger': '💢', 'angry': '😠',
    'anguished': '😧', 'signal_strength': '📶', 'arrows_counterclockwise':
    '🔄', 'arrow_heading_down': '⤵', 'arrow_heading_up': '⤴', 'art': '🎨',
    'astonished': '😲', 'athletic_shoe': '👟', 'atm': '🏧', 'car': '🚗',
    'red_car': '🚗', 'angel': '👼', 'back': '🔙',
    'badminton_racquet_and_shuttlecock': '🏸', 'dollar': '💵', 'euro': '💶',
    'pound': '💷', 'yen': '💴', 'barber': '💈', 'bath': '🛀', 'bear': '🐻',
    'heartbeat': '💓', 'beer': '🍺', 'no_bell': '🔕', 'bento': '🍱', 'bike':
    '🚲', 'bicyclist': '🚴', '8ball': '🎱', 'biohazard_sign': '☣', 'birthday':
    '🎂', 'black_circle_for_record': '⏺', 'clubs': '♣', 'diamonds': '♦',
    'arrow_double_down': '⏬', 'hearts': '♥', 'rewind': '⏪',
    'black_left__pointing_double_triangle_with_vertical_bar': '⏮',
    'arrow_backward': '◀', 'black_medium_small_square': '◾', 'question':
    '❓', 'fast_forward': '⏩',
    'black_right__pointing_double_triangle_with_vertical_bar': '⏭',
    'arrow_forward': '▶',
    'black_right__pointing_triangle_with_double_vertical_bar': '⏯',
    'arrow_right': '➡', 'spades': '♠', 'black_square_for_stop': '⏹',
    'sunny': '☀', 'phone': '☎', 'recycle': '♻', 'arrow_double_up': '⏫',
    'busstop': '🚏', 'date': '📅', 'flags': '🎏', 'cat2': '🐈', 'joy_cat': '😹',
    'smirk_cat': '😼', 'chart_with_downwards_trend': '📉',
    'chart_with_upwards_trend': '📈', 'chart': '💹', 'mega': '📣',
    'checkered_flag': '🏁', 'accept': '🉑', 'ideograph_advantage': '🉐',
    'congratulations': '㊗', 'secret': '㊙', 'm': 'Ⓜ', 'city_sunset': '🌆',
    'clapper': '🎬', 'clap': '👏', 'beers': '🍻', 'clock830': '🕣', 'clock8':
    '🕗', 'clock1130': '🕦', 'clock11': '🕚', 'clock530': '🕠', 'clock5': '🕔',
    'clock430': '🕟', 'clock4': '🕓', 'clock930': '🕤', 'clock9': '🕘',
    'clock130': '🕜', 'clock1': '🕐', 'clock730': '🕢', 'clock7': '🕖',
    'clock630': '🕡', 'clock6': '🕕', 'clock1030': '🕥', 'clock10': '🕙',
    'clock330': '🕞', 'clock3': '🕒', 'clock1230': '🕧', 'clock12': '🕛',
    'clock230': '🕝', 'clock2': '🕑', 'arrows_clockwise': '🔃', 'repeat': '🔁',
    'repeat_one': '🔂', 'closed_lock_with_key': '🔐', 'mailbox_closed': '📪',
    'mailbox': '📫', 'cloud_with_tornado': '🌪', 'cocktail': '🍸', 'boom': '💥',
    'compression': '🗜', 'confounded': '😖', 'confused': '😕', 'rice': '🍚',
    'cow2': '🐄', 'cricket_bat_and_ball': '🏏', 'x': '❌', 'cry': '😢', 'curry':
    '🍛', 'dagger_knife': '🗡', 'dancer': '💃', 'dark_sunglasses': '🕶', 'dash':
    '💨', 'truck': '🚚', 'derelict_house_building': '🏚',
    'diamond_shape_with_a_dot_inside': '💠', 'dart': '🎯',
    'disappointed_relieved': '😥', 'disappointed': '😞', 'do_not_litter': '🚯',
    'dog2': '🐕', 'flipper': '🐬', 'loop': '➿', 'bangbang': '‼',
    'double_vertical_bar': '⏸', 'dove_of_peace': '🕊',
    'small_red_triangle_down': '🔻', 'arrow_down_small': '🔽', 'arrow_down':
    '⬇', 'dromedary_camel': '🐪', 'e__mail': '📧', 'corn': '🌽', 'ear_of_rice':
    '🌾', 'earth_americas': '🌎', 'earth_asia': '🌏', 'earth_africa': '🌍',
    'eight_pointed_black_star': '✴', 'eight_spoked_asterisk': '✳',
    'eject_symbol': '⏏', 'bulb': '💡',
    'emoji_modifier_fitzpatrick_type__1__2': '🏻',
    'emoji_modifier_fitzpatrick_type__3': '🏼',
    'emoji_modifier_fitzpatrick_type__4': '🏽',
    'emoji_modifier_fitzpatrick_type__5': '🏾',
    'emoji_modifier_fitzpatrick_type__6': '🏿', 'end': '🔚', 'email': '✉',
    'european_castle': '🏰', 'european_post_office': '🏤', 'interrobang': '⁉',
    'expressionless': '😑', 'eyeglasses': '👓', 'massage': '💆', 'yum': '😋',
    'scream': '😱', 'kissing_heart': '😘', 'sweat': '😓',
    'face_with_head__bandage': '🤕', 'triumph': '😤', 'mask': '😷', 'no_good':
    '🙅', 'ok_woman': '🙆', 'open_mouth': '😮', 'cold_sweat': '😰',
    'stuck_out_tongue': '😛', 'stuck_out_tongue_closed_eyes': '😝',
    'stuck_out_tongue_winking_eye': '😜', 'joy': '😂', 'no_mouth': '😶',
    'santa': '🎅', 'fax': '📠', 'fearful': '😨', 'field_hockey_stick_and_ball':
    '🏑', 'first_quarter_moon_with_face': '🌛', 'fish_cake': '🍥',
    'fishing_pole_and_fish': '🎣', 'facepunch': '👊', 'punch': '👊',
    'flag_for_afghanistan': '🇦🇫', 'flag_for_albania': '🇦🇱',
    'flag_for_algeria': '🇩🇿', 'flag_for_american_samoa': '🇦🇸',
    'flag_for_andorra': '🇦🇩', 'flag_for_angola': '🇦🇴', 'flag_for_anguilla':
    '🇦🇮', 'flag_for_antarctica': '🇦🇶', 'flag_for_antigua_&_barbuda': '🇦🇬',
    'flag_for_argentina': '🇦🇷', 'flag_for_armenia': '🇦🇲', 'flag_for_aruba':
    '🇦🇼', 'flag_for_ascension_island': '🇦🇨', 'flag_for_australia': '🇦🇺',
    'flag_for_austria': '🇦🇹', 'flag_for_azerbaijan': '🇦🇿',
    'flag_for_bahamas': '🇧🇸', 'flag_for_bahrain': '🇧🇭',
    'flag_for_bangladesh': '🇧🇩', 'flag_for_barbados': '🇧🇧',
    'flag_for_belarus': '🇧🇾', 'flag_for_belgium': '🇧🇪', 'flag_for_belize':
    '🇧🇿', 'flag_for_benin': '🇧🇯', 'flag_for_bermuda': '🇧🇲',
    'flag_for_bhutan': '🇧🇹', 'flag_for_bolivia': '🇧🇴',
    'flag_for_bosnia_&_herzegovina': '🇧🇦', 'flag_for_botswana': '🇧🇼',
    'flag_for_bouvet_island': '🇧🇻', 'flag_for_brazil': '🇧🇷',
    'flag_for_british_indian_ocean_territory': '🇮🇴',
    'flag_for_british_virgin_islands': '🇻🇬', 'flag_for_brunei': '🇧🇳',
    'flag_for_bulgaria': '🇧🇬', 'flag_for_burkina_faso': '🇧🇫',
    'flag_for_burundi': '🇧🇮', 'flag_for_cambodia': '🇰🇭',
    'flag_for_cameroon': '🇨🇲', 'flag_for_canada': '🇨🇦',
    'flag_for_canary_islands': '🇮🇨', 'flag_for_cape_verde': '🇨🇻',
    'flag_for_caribbean_netherlands': '🇧🇶', 'flag_for_cayman_islands': '🇰🇾',
    'flag_for_central_african_republic': '🇨🇫', 'flag_for_ceuta_&_melilla':
    '🇪🇦', 'flag_for_chad': '🇹🇩', 'flag_for_chile': '🇨🇱', 'flag_for_china':
    '🇨🇳', 'flag_for_christmas_island': '🇨🇽', 'flag_for_clipperton_island':
    '🇨🇵', 'flag_for_cocos__islands': '🇨🇨', 'flag_for_colombia': '🇨🇴',
    'flag_for_comoros': '🇰🇲', 'flag_for_congo____brazzaville': '🇨🇬',
    'flag_for_congo____kinshasa': '🇨🇩', 'flag_for_cook_islands': '🇨🇰',
    'flag_for_costa_rica': '🇨🇷', 'flag_for_croatia': '🇭🇷', 'flag_for_cuba':
    '🇨🇺', 'flag_for_curaçao': '🇨🇼', 'flag_for_cyprus': '🇨🇾',
    'flag_for_czech_republic': '🇨🇿', 'flag_for_côte_d’ivoire': '🇨🇮',
    'flag_for_denmark': '🇩🇰', 'flag_for_diego_garcia': '🇩🇬',
    'flag_for_djibouti': '🇩🇯', 'flag_for_dominica': '🇩🇲',
    'flag_for_dominican_republic': '🇩🇴', 'flag_for_ecuador': '🇪🇨',
    'flag_for_egypt': '🇪🇬', 'flag_for_el_salvador': '🇸🇻',
    'flag_for_equatorial_guinea': '🇬🇶', 'flag_for_eritrea': '🇪🇷',
    'flag_for_estonia': '🇪🇪', 'flag_for_ethiopia': '🇪🇹',
    'flag_for_european_union': '🇪🇺', 'flag_for_falkland_islands': '🇫🇰',
    'flag_for_faroe_islands': '🇫🇴', 'flag_for_fiji': '🇫🇯',
    'flag_for_finland': '🇫🇮', 'flag_for_france': '🇫🇷',
    'flag_for_french_guiana': '🇬🇫', 'flag_for_french_polynesia': '🇵🇫',
    'flag_for_french_southern_territories': '🇹🇫', 'flag_for_gabon': '🇬🇦',
    'flag_for_gambia': '🇬🇲', 'flag_for_georgia': '🇬🇪', 'flag_for_germany':
    '🇩🇪', 'flag_for_ghana': '🇬🇭', 'flag_for_gibraltar': '🇬🇮',
    'flag_for_greece': '🇬🇷', 'flag_for_greenland': '🇬🇱', 'flag_for_grenada':
    '🇬🇩', 'flag_for_guadeloupe': '🇬🇵', 'flag_for_guam': '🇬🇺',
    'flag_for_guatemala': '🇬🇹', 'flag_for_guernsey': '🇬🇬',
    'flag_for_guinea': '🇬🇳', 'flag_for_guinea__bissau': '🇬🇼',
    'flag_for_guyana': '🇬🇾', 'flag_for_haiti': '🇭🇹',
    'flag_for_heard_&_mcdonald_islands': '🇭🇲', 'flag_for_honduras': '🇭🇳',
    'flag_for_hong_kong': '🇭🇰', 'flag_for_hungary': '🇭🇺',
    'flag_for_iceland': '🇮🇸', 'flag_for_india': '🇮🇳', 'flag_for_indonesia':
    '🇮🇩', 'flag_for_iran': '🇮🇷', 'flag_for_iraq': '🇮🇶', 'flag_for_ireland':
    '🇮🇪', 'flag_for_isle_of_man': '🇮🇲', 'flag_for_israel': '🇮🇱',
    'flag_for_italy': '🇮🇹', 'flag_for_jamaica': '🇯🇲', 'flag_for_japan':
    '🇯🇵', 'flag_for_jersey': '🇯🇪', 'flag_for_jordan': '🇯🇴',
    'flag_for_kazakhstan': '🇰🇿', 'flag_for_kenya': '🇰🇪',
    'flag_for_kiribati': '🇰🇮', 'flag_for_kosovo': '🇽🇰', 'flag_for_kuwait':
    '🇰🇼', 'flag_for_kyrgyzstan': '🇰🇬', 'flag_for_laos': '🇱🇦',
    'flag_for_latvia': '🇱🇻', 'flag_for_lebanon': '🇱🇧', 'flag_for_lesotho':
    '🇱🇸', 'flag_for_liberia': '🇱🇷', 'flag_for_libya': '🇱🇾',
    'flag_for_liechtenstein': '🇱🇮', 'flag_for_lithuania': '🇱🇹',
    'flag_for_luxembourg': '🇱🇺', 'flag_for_macau': '🇲🇴',
    'flag_for_macedonia': '🇲🇰', 'flag_for_madagascar': '🇲🇬',
    'flag_for_malawi': '🇲🇼', 'flag_for_malaysia': '🇲🇾', 'flag_for_maldives':
    '🇲🇻', 'flag_for_mali': '🇲🇱', 'flag_for_malta': '🇲🇹',
    'flag_for_marshall_islands': '🇲🇭', 'flag_for_martinique': '🇲🇶',
    'flag_for_mauritania': '🇲🇷', 'flag_for_mauritius': '🇲🇺',
    'flag_for_mayotte': '🇾🇹', 'flag_for_mexico': '🇲🇽',
    'flag_for_micronesia': '🇫🇲', 'flag_for_moldova': '🇲🇩',
    'flag_for_monaco': '🇲🇨', 'flag_for_mongolia': '🇲🇳',
    'flag_for_montenegro': '🇲🇪', 'flag_for_montserrat': '🇲🇸',
    'flag_for_morocco': '🇲🇦', 'flag_for_mozambique': '🇲🇿',
    'flag_for_myanmar': '🇲🇲', 'flag_for_namibia': '🇳🇦', 'flag_for_nauru':
    '🇳🇷', 'flag_for_nepal': '🇳🇵', 'flag_for_netherlands': '🇳🇱',
    'flag_for_new_caledonia': '🇳🇨', 'flag_for_new_zealand': '🇳🇿',
    'flag_for_nicaragua': '🇳🇮', 'flag_for_niger': '🇳🇪', 'flag_for_nigeria':
    '🇳🇬', 'flag_for_niue': '🇳🇺', 'flag_for_norfolk_island': '🇳🇫',
    'flag_for_north_korea': '🇰🇵', 'flag_for_northern_mariana_islands': '🇲🇵',
    'flag_for_norway': '🇳🇴', 'flag_for_oman': '🇴🇲', 'flag_for_pakistan':
    '🇵🇰', 'flag_for_palau': '🇵🇼', 'flag_for_palestinian_territories': '🇵🇸',
    'flag_for_panama': '🇵🇦', 'flag_for_papua_new_guinea': '🇵🇬',
    'flag_for_paraguay': '🇵🇾', 'flag_for_peru': '🇵🇪',
    'flag_for_philippines': '🇵🇭', 'flag_for_pitcairn_islands': '🇵🇳',
    'flag_for_poland': '🇵🇱', 'flag_for_portugal': '🇵🇹',
    'flag_for_puerto_rico': '🇵🇷', 'flag_for_qatar': '🇶🇦',
    'flag_for_romania': '🇷🇴', 'flag_for_russia': '🇷🇺', 'flag_for_rwanda':
    '🇷🇼', 'flag_for_réunion': '🇷🇪', 'flag_for_samoa': '🇼🇸',
    'flag_for_san_marino': '🇸🇲', 'flag_for_saudi_arabia': '🇸🇦',
    'flag_for_senegal': '🇸🇳', 'flag_for_serbia': '🇷🇸',
    'flag_for_seychelles': '🇸🇨', 'flag_for_sierra_leone': '🇸🇱',
    'flag_for_singapore': '🇸🇬', 'flag_for_sint_maarten': '🇸🇽',
    'flag_for_slovakia': '🇸🇰', 'flag_for_slovenia': '🇸🇮',
    'flag_for_solomon_islands': '🇸🇧', 'flag_for_somalia': '🇸🇴',
    'flag_for_south_africa': '🇿🇦',
    'flag_for_south_georgia_&_south_sandwich_islands': '🇬🇸',
    'flag_for_south_korea': '🇰🇷', 'flag_for_south_sudan': '🇸🇸',
    'flag_for_spain': '🇪🇸', 'flag_for_sri_lanka': '🇱🇰',
    'flag_for_st._barthélemy': '🇧🇱', 'flag_for_st._helena': '🇸🇭',
    'flag_for_st._kitts_&_nevis': '🇰🇳', 'flag_for_st._lucia': '🇱🇨',
    'flag_for_st._martin': '🇲🇫', 'flag_for_st._pierre_&_miquelon': '🇵🇲',
    'flag_for_st._vincent_&_grenadines': '🇻🇨', 'flag_for_sudan': '🇸🇩',
    'flag_for_suriname': '🇸🇷', 'flag_for_svalbard_&_jan_mayen': '🇸🇯',
    'flag_for_swaziland': '🇸🇿', 'flag_for_sweden': '🇸🇪',
    'flag_for_switzerland': '🇨🇭', 'flag_for_syria': '🇸🇾',
    'flag_for_são_tomé_&_príncipe': '🇸🇹', 'flag_for_taiwan': '🇹🇼',
    'flag_for_tajikistan': '🇹🇯', 'flag_for_tanzania': '🇹🇿',
    'flag_for_thailand': '🇹🇭', 'flag_for_timor__leste': '🇹🇱',
    'flag_for_togo': '🇹🇬', 'flag_for_tokelau': '🇹🇰', 'flag_for_tonga': '🇹🇴',
    'flag_for_trinidad_&_tobago': '🇹🇹', 'flag_for_tristan_da_cunha': '🇹🇦',
    'flag_for_tunisia': '🇹🇳', 'flag_for_turkey': '🇹🇷',
    'flag_for_turkmenistan': '🇹🇲', 'flag_for_turks_&_caicos_islands': '🇹🇨',
    'flag_for_tuvalu': '🇹🇻', 'flag_for_u.s._outlying_islands': '🇺🇲',
    'flag_for_u.s._virgin_islands': '🇻🇮', 'flag_for_uganda': '🇺🇬',
    'flag_for_ukraine': '🇺🇦', 'flag_for_united_arab_emirates': '🇦🇪',
    'flag_for_united_kingdom': '🇬🇧', 'flag_for_united_states': '🇺🇸',
    'flag_for_uruguay': '🇺🇾', 'flag_for_uzbekistan': '🇺🇿',
    'flag_for_vanuatu': '🇻🇺', 'flag_for_vatican_city': '🇻🇦',
    'flag_for_venezuela': '🇻🇪', 'flag_for_vietnam': '🇻🇳',
    'flag_for_wallis_&_futuna': '🇼🇫', 'flag_for_western_sahara': '🇪🇭',
    'flag_for_yemen': '🇾🇪', 'flag_for_zambia': '🇿🇲', 'flag_for_zimbabwe':
    '🇿🇼', 'flag_for_åland_islands': '🇦🇽', 'golf': '⛳', 'fleur__de__lis':
    '⚜', 'muscle': '💪', 'flushed': '😳', 'frame_with_picture': '🖼', 'fries':
    '🍟', 'frog': '🐸', 'hatched_chick': '🐥', 'frowning': '😦', 'fuelpump':
    '⛽', 'full_moon_with_face': '🌝', 'gem': '💎', 'star2': '🌟', 'golfer':
    '🏌', 'mortar_board': '🎓', 'grimacing': '😬', 'smile_cat': '😸',
    'grinning': '😀', 'grin': '😁', 'heartpulse': '💗', 'guardsman': '💂',
    'haircut': '💇', 'hamster': '🐹', 'raising_hand': '🙋', 'headphones': '🎧',
    'hear_no_evil': '🙉', 'cupid': '💘', 'gift_heart': '💝', 'heart': '❤',
    'exclamation': '❗', 'heavy_exclamation_mark': '❗',
    'heavy_heart_exclamation_mark_ornament': '❣', 'o': '⭕', 'helm_symbol':
    '⎈', 'helmet_with_white_cross': '⛑', 'high_heel': '👠',
    'bullettrain_side': '🚄', 'bullettrain_front': '🚅', 'high_brightness':
    '🔆', 'zap': '⚡', 'hocho': '🔪', 'knife': '🔪', 'bee': '🐝',
    'traffic_light': '🚥', 'racehorse': '🐎', 'coffee': '☕', 'hotsprings':
    '♨', 'hourglass': '⌛', 'hourglass_flowing_sand': '⏳', 'house_buildings':
    '🏘', '100': '💯', 'hushed': '😯', 'ice_hockey_stick_and_puck': '🏒', 'imp':
    '👿', 'information_desk_person': '💁', 'information_source': 'ℹ',
    'capital_abcd': '🔠', 'abc': '🔤', 'abcd': '🔡', '1234': '🔢', 'symbols':
    '🔣', 'izakaya_lantern': '🏮', 'lantern': '🏮', 'jack_o_lantern': '🎃',
    'dolls': '🎎', 'japanese_goblin': '👺', 'japanese_ogre': '👹', 'beginner':
    '🔰', 'zero': '0️⃣', 'one': '1️⃣', 'ten': '🔟', 'two': '2️⃣', 'three':
    '3️⃣', 'four': '4️⃣', 'five': '5️⃣', 'six': '6️⃣', 'seven': '7️⃣',
    'eight': '8️⃣', 'nine': '9️⃣', 'couplekiss': '💏', 'kissing_cat': '😽',
    'kissing': '😗', 'kissing_closed_eyes': '😚', 'kissing_smiling_eyes': '😙',
    'beetle': '🐞', 'large_blue_circle': '🔵', 'last_quarter_moon_with_face':
    '🌜', 'leaves': '🍃', 'mag': '🔍', 'left_right_arrow': '↔',
    'leftwards_arrow_with_hook': '↩', 'arrow_left': '⬅', 'lock': '🔒',
    'lock_with_ink_pen': '🔏', 'sob': '😭', 'low_brightness': '🔅',
    'lower_left_ballpoint_pen': '🖊', 'lower_left_crayon': '🖍',
    'lower_left_fountain_pen': '🖋', 'lower_left_paintbrush': '🖌', 'mahjong':
    '🀄', 'couple': '👫', 'man_in_business_suit_levitating': '🕴',
    'man_with_gua_pi_mao': '👲', 'man_with_turban': '👳', 'mans_shoe': '👞',
    'shoe': '👞', 'menorah_with_nine_branches': '🕎', 'mens': '🚹', 'minidisc':
    '💽', 'iphone': '📱', 'calling': '📲', 'money__mouth_face': '🤑',
    'moneybag': '💰', 'rice_scene': '🎑', 'mountain_bicyclist': '🚵', 'mouse2':
    '🐁', 'lips': '👄', 'moyai': '🗿', 'notes': '🎶', 'nail_care': '💅', 'ab':
    '🆎', 'negative_squared_cross_mark': '❎', 'a': '🅰', 'b': '🅱', 'o2': '🅾',
    'parking': '🅿', 'new_moon_with_face': '🌚', 'no_entry_sign': '🚫',
    'underage': '🔞', 'non__potable_water': '🚱', 'arrow_upper_right': '↗',
    'arrow_upper_left': '↖', 'office': '🏢', 'older_man': '👴', 'older_woman':
    '👵', 'om_symbol': '🕉', 'on': '🔛', 'book': '📖', 'unlock': '🔓',
    'mailbox_with_no_mail': '📭', 'mailbox_with_mail': '📬', 'cd': '💿',
    'tada': '🎉', 'feet': '🐾', 'walking': '🚶', 'pencil2': '✏', 'pensive':
    '😔', 'persevere': '😣', 'bow': '🙇', 'raised_hands': '🙌',
    'person_with_ball': '⛹', 'person_with_blond_hair': '👱', 'pray': '🙏',
    'person_with_pouting_face': '🙎', 'computer': '💻', 'pig2': '🐖', 'hankey':
    '💩', 'poop': '💩', 'shit': '💩', 'bamboo': '🎍', 'gun': '🔫', 'black_joker':
    '🃏', 'rotating_light': '🚨', 'cop': '👮', 'stew': '🍲', 'pouch': '👝',
    'pouting_cat': '😾', 'rage': '😡', 'put_litter_in_its_place': '🚮',
    'rabbit2': '🐇', 'racing_motorcycle': '🏍', 'radioactive_sign': '☢',
    'fist': '✊', 'hand': '✋', 'raised_hand_with_fingers_splayed': '🖐',
    'raised_hand_with_part_between_middle_and_ring_fingers': '🖖',
    'blue_car': '🚙', 'apple': '🍎', 'relieved': '😌',
    'reversed_hand_with_middle_finger_extended': '🖕', 'mag_right': '🔎',
    'arrow_right_hook': '↪', 'sweet_potato': '🍠', 'robot': '🤖',
    'rolled__up_newspaper': '🗞', 'rowboat': '🚣', 'runner': '🏃', 'running':
    '🏃', 'running_shirt_with_sash': '🎽', 'boat': '⛵', 'scales': '⚖',
    'school_satchel': '🎒', 'scorpius': '♏', 'see_no_evil': '🙈', 'sheep':
    '🐑', 'stars': '🌠', 'cake': '🍰', 'six_pointed_star': '🔯', 'ski': '🎿',
    'sleeping_accommodation': '🛌', 'sleeping': '😴', 'sleepy': '😪',
    'sleuth_or_spy': '🕵', 'heart_eyes_cat': '😻', 'smiley_cat': '😺',
    'innocent': '😇', 'heart_eyes': '😍', 'smiling_imp': '😈', 'smiley': '😃',
    'sweat_smile': '😅', 'smile': '😄', 'laughing': '😆', 'satisfied': '😆',
    'blush': '😊', 'smirk': '😏', 'smoking': '🚬', 'snow_capped_mountain': '🏔',
    'soccer': '⚽', 'icecream': '🍦', 'soon': '🔜', 'arrow_lower_right': '↘',
    'arrow_lower_left': '↙', 'speak_no_evil': '🙊', 'speaker': '🔈', 'mute':
    '🔇', 'sound': '🔉', 'loud_sound': '🔊', 'speaking_head_in_silhouette':
    '🗣', 'spiral_calendar_pad': '🗓', 'spiral_note_pad': '🗒', 'shell': '🐚',
    'sweat_drops': '💦', 'u5272': '🈹', 'u5408': '🈴', 'u55b6': '🈺', 'u6307':
    '🈯', 'u6708': '🈷', 'u6709': '🈶', 'u6e80': '🈵', 'u7121': '🈚', 'u7533':
    '🈸', 'u7981': '🈲', 'u7a7a': '🈳', 'cl': '🆑', 'cool': '🆒', 'free': '🆓',
    'id': '🆔', 'koko': '🈁', 'sa': '🈂', 'new': '🆕', 'ng': '🆖', 'ok': '🆗',
    'sos': '🆘', 'up': '🆙', 'vs': '🆚', 'steam_locomotive': '🚂', 'ramen': '🍜',
    'partly_sunny': '⛅', 'city_sunrise': '🌇', 'surfer': '🏄', 'swimmer': '🏊',
    'shirt': '👕', 'tshirt': '👕', 'table_tennis_paddle_and_ball': '🏓', 'tea':
    '🍵', 'tv': '📺', 'three_button_mouse': '🖱', '+1': '👍', 'thumbsup': '👍',
    '__1': '👎', '-1': '👎', 'thumbsdown': '👎', 'thunder_cloud_and_rain': '⛈',
    'tiger2': '🐅', 'tophat': '🎩', 'top': '🔝', 'tm': '™', 'train2': '🚆',
    'triangular_flag_on_post': '🚩', 'trident': '🔱',
    'twisted_rightwards_arrows': '🔀', 'unamused': '😒', 'small_red_triangle':
    '🔺', 'arrow_up_small': '🔼', 'arrow_up_down': '↕', 'upside__down_face':
    '🙃', 'arrow_up': '⬆', 'v': '✌', 'vhs': '📼', 'wc': '🚾', 'ocean': '🌊',
    'waving_black_flag': '🏴', 'wave': '👋', 'waving_white_flag': '🏳', 'moon':
    '🌔', 'scream_cat': '🙀', 'weary': '😩', 'weight_lifter': '🏋', 'whale2':
    '🐋', 'wheelchair': '♿', 'point_down': '👇', 'grey_exclamation': '❕',
    'white_frowning_face': '☹', 'white_check_mark': '✅', 'point_left': '👈',
    'white_medium_small_square': '◽', 'star': '⭐', 'grey_question': '❔',
    'point_right': '👉', 'relaxed': '☺', 'white_sun_behind_cloud': '🌥',
    'white_sun_behind_cloud_with_rain': '🌦', 'white_sun_with_small_cloud':
    '🌤', 'point_up_2': '👆', 'point_up': '☝', 'wind_blowing_face': '🌬',
    'wink': '😉', 'wolf': '🐺', 'dancers': '👯', 'boot': '👢', 'womans_clothes':
    '👚', 'womans_hat': '👒', 'sandal': '👡', 'womens': '🚺', 'worried': '😟',
    'gift': '🎁', 'zipper__mouth_face': '🤐', 'regional_indicator_a': '🇦',
    'regional_indicator_b': '🇧', 'regional_indicator_c': '🇨',
    'regional_indicator_d': '🇩', 'regional_indicator_e': '🇪',
    'regional_indicator_f': '🇫', 'regional_indicator_g': '🇬',
    'regional_indicator_h': '🇭', 'regional_indicator_i': '🇮',
    'regional_indicator_j': '🇯', 'regional_indicator_k': '🇰',
    'regional_indicator_l': '🇱', 'regional_indicator_m': '🇲',
    'regional_indicator_n': '🇳', 'regional_indicator_o': '🇴',
    'regional_indicator_p': '🇵', 'regional_indicator_q': '🇶',
    'regional_indicator_r': '🇷', 'regional_indicator_s': '🇸',
    'regional_indicator_t': '🇹', 'regional_indicator_u': '🇺',
    'regional_indicator_v': '🇻', 'regional_indicator_w': '🇼',
    'regional_indicator_x': '🇽', 'regional_indicator_y': '🇾',
    'regional_indicator_z': '🇿'}

LEGACY_WINDOWS_SUBSTITUTIONS = {ROUNDED: SQUARE, MINIMAL_HEAVY_HEAD: MINIMAL, SIMPLE_HEAVY: SIMPLE, HEAVY:
    SQUARE, HEAVY_EDGE: SQUARE, HEAVY_HEAD: SQUARE}

PLAIN_HEADED_SUBSTITUTIONS = {HEAVY_HEAD: SQUARE, SQUARE_DOUBLE_HEAD: SQUARE, MINIMAL_DOUBLE_HEAD:
    MINIMAL, MINIMAL_HEAVY_HEAD: MINIMAL, ASCII_DOUBLE_HEAD: ASCII2}

BOXES = ['ASCII', 'ASCII2', 'ASCII_DOUBLE_HEAD', 'SQUARE', 'SQUARE_DOUBLE_HEAD',
    'MINIMAL', 'MINIMAL_HEAVY_HEAD', 'MINIMAL_DOUBLE_HEAD', 'SIMPLE',
    'SIMPLE_HEAD', 'SIMPLE_HEAVY', 'HORIZONTALS', 'ROUNDED', 'HEAVY',
    'HEAVY_EDGE', 'HEAVY_HEAD', 'DOUBLE', 'DOUBLE_EDGE', 'MARKDOWN']

STANDARD = (1)

EIGHT_BIT = (2)

TRUECOLOR = (3)

ANSI_COLOR_NAMES = {'black': 0, 'red': 1, 'green': 2, 'yellow': 3, 'blue': 4, 'magenta': 5,
    'cyan': 6, 'white': 7, 'bright_black': 8, 'bright_red': 9,
    'bright_green': 10, 'bright_yellow': 11, 'bright_blue': 12,
    'bright_magenta': 13, 'bright_cyan': 14, 'bright_white': 15, 'grey0': 
    16, 'gray0': 16, 'navy_blue': 17, 'dark_blue': 18, 'blue3': 20, 'blue1':
    21, 'dark_green': 22, 'deep_sky_blue4': 25, 'dodger_blue3': 26,
    'dodger_blue2': 27, 'green4': 28, 'spring_green4': 29, 'turquoise4': 30,
    'deep_sky_blue3': 32, 'dodger_blue1': 33, 'green3': 40, 'spring_green3':
    41, 'dark_cyan': 36, 'light_sea_green': 37, 'deep_sky_blue2': 38,
    'deep_sky_blue1': 39, 'spring_green2': 47, 'cyan3': 43,
    'dark_turquoise': 44, 'turquoise2': 45, 'green1': 46, 'spring_green1': 
    48, 'medium_spring_green': 49, 'cyan2': 50, 'cyan1': 51, 'dark_red': 88,
    'deep_pink4': 125, 'purple4': 55, 'purple3': 56, 'blue_violet': 57,
    'orange4': 94, 'grey37': 59, 'gray37': 59, 'medium_purple4': 60,
    'slate_blue3': 62, 'royal_blue1': 63, 'chartreuse4': 64,
    'dark_sea_green4': 71, 'pale_turquoise4': 66, 'steel_blue': 67,
    'steel_blue3': 68, 'cornflower_blue': 69, 'chartreuse3': 76,
    'cadet_blue': 73, 'sky_blue3': 74, 'steel_blue1': 81, 'pale_green3': 
    114, 'sea_green3': 78, 'aquamarine3': 79, 'medium_turquoise': 80,
    'chartreuse2': 112, 'sea_green2': 83, 'sea_green1': 85, 'aquamarine1': 
    122, 'dark_slate_gray2': 87, 'dark_magenta': 91, 'dark_violet': 128,
    'purple': 129, 'light_pink4': 95, 'plum4': 96, 'medium_purple3': 98,
    'slate_blue1': 99, 'yellow4': 106, 'wheat4': 101, 'grey53': 102,
    'gray53': 102, 'light_slate_grey': 103, 'light_slate_gray': 103,
    'medium_purple': 104, 'light_slate_blue': 105, 'dark_olive_green3': 149,
    'dark_sea_green': 108, 'light_sky_blue3': 110, 'sky_blue2': 111,
    'dark_sea_green3': 150, 'dark_slate_gray3': 116, 'sky_blue1': 117,
    'chartreuse1': 118, 'light_green': 120, 'pale_green1': 156,
    'dark_slate_gray1': 123, 'red3': 160, 'medium_violet_red': 126,
    'magenta3': 164, 'dark_orange3': 166, 'indian_red': 167, 'hot_pink3': 
    168, 'medium_orchid3': 133, 'medium_orchid': 134, 'medium_purple2': 140,
    'dark_goldenrod': 136, 'light_salmon3': 173, 'rosy_brown': 138,
    'grey63': 139, 'gray63': 139, 'medium_purple1': 141, 'gold3': 178,
    'dark_khaki': 143, 'navajo_white3': 144, 'grey69': 145, 'gray69': 145,
    'light_steel_blue3': 146, 'light_steel_blue': 147, 'yellow3': 184,
    'dark_sea_green2': 157, 'light_cyan3': 152, 'light_sky_blue1': 153,
    'green_yellow': 154, 'dark_olive_green2': 155, 'dark_sea_green1': 193,
    'pale_turquoise1': 159, 'deep_pink3': 162, 'magenta2': 200, 'hot_pink2':
    169, 'orchid': 170, 'medium_orchid1': 207, 'orange3': 172,
    'light_pink3': 174, 'pink3': 175, 'plum3': 176, 'violet': 177,
    'light_goldenrod3': 179, 'tan': 180, 'misty_rose3': 181, 'thistle3': 
    182, 'plum2': 183, 'khaki3': 185, 'light_goldenrod2': 222,
    'light_yellow3': 187, 'grey84': 188, 'gray84': 188, 'light_steel_blue1':
    189, 'yellow2': 190, 'dark_olive_green1': 192, 'honeydew2': 194,
    'light_cyan1': 195, 'red1': 196, 'deep_pink2': 197, 'deep_pink1': 199,
    'magenta1': 201, 'orange_red1': 202, 'indian_red1': 204, 'hot_pink': 
    206, 'dark_orange': 208, 'salmon1': 209, 'light_coral': 210,
    'pale_violet_red1': 211, 'orchid2': 212, 'orchid1': 213, 'orange1': 214,
    'sandy_brown': 215, 'light_salmon1': 216, 'light_pink1': 217, 'pink1': 
    218, 'plum1': 219, 'gold1': 220, 'navajo_white1': 223, 'misty_rose1': 
    224, 'thistle1': 225, 'yellow1': 226, 'light_goldenrod1': 227, 'khaki1':
    228, 'wheat1': 229, 'cornsilk1': 230, 'grey100': 231, 'gray100': 231,
    'grey3': 232, 'gray3': 232, 'grey7': 233, 'gray7': 233, 'grey11': 234,
    'gray11': 234, 'grey15': 235, 'gray15': 235, 'grey19': 236, 'gray19': 
    236, 'grey23': 237, 'gray23': 237, 'grey27': 238, 'gray27': 238,
    'grey30': 239, 'gray30': 239, 'grey35': 240, 'gray35': 240, 'grey39': 
    241, 'gray39': 241, 'grey42': 242, 'gray42': 242, 'grey46': 243,
    'gray46': 243, 'grey50': 244, 'gray50': 244, 'grey54': 245, 'gray54': 
    245, 'grey58': 246, 'gray58': 246, 'grey62': 247, 'gray62': 247,
    'grey66': 248, 'gray66': 248, 'grey70': 249, 'gray70': 249, 'grey74': 
    250, 'gray74': 250, 'grey78': 251, 'gray78': 251, 'grey82': 252,
    'gray82': 252, 'grey85': 253, 'gray85': 253, 'grey89': 254, 'gray89': 
    254, 'grey93': 255, 'gray93': 255}

RE_COLOR = re.compile(
    """^
\\#([0-9a-f]{6})$|
color\\(([0-9]{1,3})\\)$|
rgb\\(([\\d\\s,]+)\\)$
"""
    , re.VERBOSE)

STYLE_ATTRIBUTES = cls.STYLE_ATTRIBUTES

NULL_STYLE = Style()

VARIANTS = {'text': '︎', 'emoji': '️'}

LOCALS_MAX_LENGTH = (10)

LOCALS_MAX_STRING = (80)

_GIBBERISH = """aihwerij235234ljsdnp34ksodfipwoe234234jlskjdf"""

NULL_FILE = NullFile()

WINDOWS_PALETTE = Palette([(12, 12, 12), (197, 15, 31), (19, 161, 14), (193, 156, 0), (0, 55,
    218), (136, 23, 152), (58, 150, 221), (204, 204, 204), (118, 118, 118),
    (231, 72, 86), (22, 198, 12), (249, 241, 165), (59, 120, 255), (180, 0,
    158), (97, 214, 214), (242, 242, 242)])

STANDARD_PALETTE = Palette([(0, 0, 0), (170, 0, 0), (0, 170, 0), (170, 85, 0), (0, 0, 170), (
    170, 0, 170), (0, 170, 170), (170, 170, 170), (85, 85, 85), (255, 85, 
    85), (85, 255, 85), (255, 255, 85), (85, 85, 255), (255, 85, 255), (85,
    255, 255), (255, 255, 255)])

EIGHT_BIT_PALETTE = Palette([(0, 0, 0), (128, 0, 0), (0, 128, 0), (128, 128, 0), (0, 0, 128), (
    128, 0, 128), (0, 128, 128), (192, 192, 192), (128, 128, 128), (255, 0,
    0), (0, 255, 0), (255, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 
    255), (255, 255, 255), (0, 0, 0), (0, 0, 95), (0, 0, 135), (0, 0, 175),
    (0, 0, 215), (0, 0, 255), (0, 95, 0), (0, 95, 95), (0, 95, 135), (0, 95,
    175), (0, 95, 215), (0, 95, 255), (0, 135, 0), (0, 135, 95), (0, 135, 
    135), (0, 135, 175), (0, 135, 215), (0, 135, 255), (0, 175, 0), (0, 175,
    95), (0, 175, 135), (0, 175, 175), (0, 175, 215), (0, 175, 255), (0, 
    215, 0), (0, 215, 95), (0, 215, 135), (0, 215, 175), (0, 215, 215), (0,
    215, 255), (0, 255, 0), (0, 255, 95), (0, 255, 135), (0, 255, 175), (0,
    255, 215), (0, 255, 255), (95, 0, 0), (95, 0, 95), (95, 0, 135), (95, 0,
    175), (95, 0, 215), (95, 0, 255), (95, 95, 0), (95, 95, 95), (95, 95, 
    135), (95, 95, 175), (95, 95, 215), (95, 95, 255), (95, 135, 0), (95, 
    135, 95), (95, 135, 135), (95, 135, 175), (95, 135, 215), (95, 135, 255
    ), (95, 175, 0), (95, 175, 95), (95, 175, 135), (95, 175, 175), (95, 
    175, 215), (95, 175, 255), (95, 215, 0), (95, 215, 95), (95, 215, 135),
    (95, 215, 175), (95, 215, 215), (95, 215, 255), (95, 255, 0), (95, 255,
    95), (95, 255, 135), (95, 255, 175), (95, 255, 215), (95, 255, 255), (
    135, 0, 0), (135, 0, 95), (135, 0, 135), (135, 0, 175), (135, 0, 215),
    (135, 0, 255), (135, 95, 0), (135, 95, 95), (135, 95, 135), (135, 95, 
    175), (135, 95, 215), (135, 95, 255), (135, 135, 0), (135, 135, 95), (
    135, 135, 135), (135, 135, 175), (135, 135, 215), (135, 135, 255), (135,
    175, 0), (135, 175, 95), (135, 175, 135), (135, 175, 175), (135, 175, 
    215), (135, 175, 255), (135, 215, 0), (135, 215, 95), (135, 215, 135),
    (135, 215, 175), (135, 215, 215), (135, 215, 255), (135, 255, 0), (135,
    255, 95), (135, 255, 135), (135, 255, 175), (135, 255, 215), (135, 255,
    255), (175, 0, 0), (175, 0, 95), (175, 0, 135), (175, 0, 175), (175, 0,
    215), (175, 0, 255), (175, 95, 0), (175, 95, 95), (175, 95, 135), (175,
    95, 175), (175, 95, 215), (175, 95, 255), (175, 135, 0), (175, 135, 95),
    (175, 135, 135), (175, 135, 175), (175, 135, 215), (175, 135, 255), (
    175, 175, 0), (175, 175, 95), (175, 175, 135), (175, 175, 175), (175, 
    175, 215), (175, 175, 255), (175, 215, 0), (175, 215, 95), (175, 215, 
    135), (175, 215, 175), (175, 215, 215), (175, 215, 255), (175, 255, 0),
    (175, 255, 95), (175, 255, 135), (175, 255, 175), (175, 255, 215), (175,
    255, 255), (215, 0, 0), (215, 0, 95), (215, 0, 135), (215, 0, 175), (
    215, 0, 215), (215, 0, 255), (215, 95, 0), (215, 95, 95), (215, 95, 135
    ), (215, 95, 175), (215, 95, 215), (215, 95, 255), (215, 135, 0), (215,
    135, 95), (215, 135, 135), (215, 135, 175), (215, 135, 215), (215, 135,
    255), (215, 175, 0), (215, 175, 95), (215, 175, 135), (215, 175, 175),
    (215, 175, 215), (215, 175, 255), (215, 215, 0), (215, 215, 95), (215, 
    215, 135), (215, 215, 175), (215, 215, 215), (215, 215, 255), (215, 255,
    0), (215, 255, 95), (215, 255, 135), (215, 255, 175), (215, 255, 215),
    (215, 255, 255), (255, 0, 0), (255, 0, 95), (255, 0, 135), (255, 0, 175
    ), (255, 0, 215), (255, 0, 255), (255, 95, 0), (255, 95, 95), (255, 95,
    135), (255, 95, 175), (255, 95, 215), (255, 95, 255), (255, 135, 0), (
    255, 135, 95), (255, 135, 135), (255, 135, 175), (255, 135, 215), (255,
    135, 255), (255, 175, 0), (255, 175, 95), (255, 175, 135), (255, 175, 
    175), (255, 175, 215), (255, 175, 255), (255, 215, 0), (255, 215, 95),
    (255, 215, 135), (255, 215, 175), (255, 215, 215), (255, 215, 255), (
    255, 255, 0), (255, 255, 95), (255, 255, 135), (255, 255, 175), (255, 
    255, 215), (255, 255, 255), (8, 8, 8), (18, 18, 18), (28, 28, 28), (38,
    38, 38), (48, 48, 48), (58, 58, 58), (68, 68, 68), (78, 78, 78), (88, 
    88, 88), (98, 98, 98), (108, 108, 108), (118, 118, 118), (128, 128, 128
    ), (138, 138, 138), (148, 148, 148), (158, 158, 158), (168, 168, 168),
    (178, 178, 178), (188, 188, 188), (198, 198, 198), (208, 208, 208), (
    218, 218, 218), (228, 228, 228), (238, 238, 238)])

_IMPORT_CWD = """"""

RE_TAGS = re.compile('((\\\\*)\\[([a-z#/@][^[]*?)])', re.VERBOSE)

RE_HANDLER = re.compile('^([\\w.]*?)(\\(.*?\\))?$')

MARKUP = ['[red]Hello World[/red]', '[magenta]Hello [b]World[/b]',
    '[bold]Bold[italic] bold and italic [/bold]italic[/italic]',
    'Click [link=https://www.willmcgugan.com]here[/link] to visit my Blog',
    ':warning-emoji: [bold red blink] DANGER![/]']

_CONTAINERS = tuple(_BRACES.keys())

_MAPPING_CONTAINERS = (dict, os._Environ, MappingProxyType, UserDict)

JSON_STR = """(?<![\\\\\\w])(?P<str>b?\\".*?(?<!\\\\)\\")"""

JSON_WHITESPACE = {' ', '\n', '\r', '\t'}

SPINNERS = {'dots': {'interval': 80, 'frames': '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'}, 'dots2': {'interval': 80,
    'frames': '⣾⣽⣻⢿⡿⣟⣯⣷'}, 'dots3': {'interval': 80, 'frames': '⠋⠙⠚⠞⠖⠦⠴⠲⠳⠓'
    }, 'dots4': {'interval': 80, 'frames': '⠄⠆⠇⠋⠙⠸⠰⠠⠰⠸⠙⠋⠇⠆'}, 'dots5': {
    'interval': 80, 'frames': '⠋⠙⠚⠒⠂⠂⠒⠲⠴⠦⠖⠒⠐⠐⠒⠓⠋'}, 'dots6': {'interval': 
    80, 'frames': '⠁⠉⠙⠚⠒⠂⠂⠒⠲⠴⠤⠄⠄⠤⠴⠲⠒⠂⠂⠒⠚⠙⠉⠁'}, 'dots7': {'interval': 80,
    'frames': '⠈⠉⠋⠓⠒⠐⠐⠒⠖⠦⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒⠓⠋⠉⠈'}, 'dots8': {'interval': 80,
    'frames': '⠁⠁⠉⠙⠚⠒⠂⠂⠒⠲⠴⠤⠄⠄⠤⠠⠠⠤⠦⠖⠒⠐⠐⠒⠓⠋⠉⠈⠈'}, 'dots9': {'interval': 80,
    'frames': '⢹⢺⢼⣸⣇⡧⡗⡏'}, 'dots10': {'interval': 80, 'frames': '⢄⢂⢁⡁⡈⡐⡠'},
    'dots11': {'interval': 100, 'frames': '⠁⠂⠄⡀⢀⠠⠐⠈'}, 'dots12': {
    'interval': 80, 'frames': ['⢀⠀', '⡀⠀', '⠄⠀', '⢂⠀', '⡂⠀', '⠅⠀', '⢃⠀',
    '⡃⠀', '⠍⠀', '⢋⠀', '⡋⠀', '⠍⠁', '⢋⠁', '⡋⠁', '⠍⠉', '⠋⠉', '⠋⠉', '⠉⠙', '⠉⠙',
    '⠉⠩', '⠈⢙', '⠈⡙', '⢈⠩', '⡀⢙', '⠄⡙', '⢂⠩', '⡂⢘', '⠅⡘', '⢃⠨', '⡃⢐', '⠍⡐',
    '⢋⠠', '⡋⢀', '⠍⡁', '⢋⠁', '⡋⠁', '⠍⠉', '⠋⠉', '⠋⠉', '⠉⠙', '⠉⠙', '⠉⠩', '⠈⢙',
    '⠈⡙', '⠈⠩', '⠀⢙', '⠀⡙', '⠀⠩', '⠀⢘', '⠀⡘', '⠀⠨', '⠀⢐', '⠀⡐', '⠀⠠', '⠀⢀',
    '⠀⡀']}, 'dots8Bit': {'interval': 80, 'frames':
    '⠀⠁⠂⠃⠄⠅⠆⠇⡀⡁⡂⡃⡄⡅⡆⡇⠈⠉⠊⠋⠌⠍⠎⠏⡈⡉⡊⡋⡌⡍⡎⡏⠐⠑⠒⠓⠔⠕⠖⠗⡐⡑⡒⡓⡔⡕⡖⡗⠘⠙⠚⠛⠜⠝⠞⠟⡘⡙⡚⡛⡜⡝⡞⡟⠠⠡⠢⠣⠤⠥⠦⠧⡠⡡⡢⡣⡤⡥⡦⡧⠨⠩⠪⠫⠬⠭⠮⠯⡨⡩⡪⡫⡬⡭⡮⡯⠰⠱⠲⠳⠴⠵⠶⠷⡰⡱⡲⡳⡴⡵⡶⡷⠸⠹⠺⠻⠼⠽⠾⠿⡸⡹⡺⡻⡼⡽⡾⡿⢀⢁⢂⢃⢄⢅⢆⢇⣀⣁⣂⣃⣄⣅⣆⣇⢈⢉⢊⢋⢌⢍⢎⢏⣈⣉⣊⣋⣌⣍⣎⣏⢐⢑⢒⢓⢔⢕⢖⢗⣐⣑⣒⣓⣔⣕⣖⣗⢘⢙⢚⢛⢜⢝⢞⢟⣘⣙⣚⣛⣜⣝⣞⣟⢠⢡⢢⢣⢤⢥⢦⢧⣠⣡⣢⣣⣤⣥⣦⣧⢨⢩⢪⢫⢬⢭⢮⢯⣨⣩⣪⣫⣬⣭⣮⣯⢰⢱⢲⢳⢴⢵⢶⢷⣰⣱⣲⣳⣴⣵⣶⣷⢸⢹⢺⢻⢼⢽⢾⢿⣸⣹⣺⣻⣼⣽⣾⣿'
    }, 'line': {'interval': 130, 'frames': ['-', '\\', '|', '/']}, 'line2':
    {'interval': 100, 'frames': '⠂-–—–-'}, 'pipe': {'interval': 100,
    'frames': '┤┘┴└├┌┬┐'}, 'simpleDots': {'interval': 400, 'frames': ['.  ',
    '.. ', '...', '   ']}, 'simpleDotsScrolling': {'interval': 200,
    'frames': ['.  ', '.. ', '...', ' ..', '  .', '   ']}, 'star': {
    'interval': 70, 'frames': '✶✸✹✺✹✷'}, 'star2': {'interval': 80, 'frames':
    '+x*'}, 'flip': {'interval': 70, 'frames': "___-``'´-___"}, 'hamburger':
    {'interval': 100, 'frames': '☱☲☴'}, 'growVertical': {'interval': 120,
    'frames': '▁▃▄▅▆▇▆▅▄▃'}, 'growHorizontal': {'interval': 120, 'frames':
    '▏▎▍▌▋▊▉▊▋▌▍▎'}, 'balloon': {'interval': 140, 'frames': ' .oO@* '},
    'balloon2': {'interval': 120, 'frames': '.oO°Oo.'}, 'noise': {
    'interval': 100, 'frames': '▓▒░'}, 'bounce': {'interval': 120, 'frames':
    '⠁⠂⠄⠂'}, 'boxBounce': {'interval': 120, 'frames': '▖▘▝▗'}, 'boxBounce2':
    {'interval': 100, 'frames': '▌▀▐▄'}, 'triangle': {'interval': 50,
    'frames': '◢◣◤◥'}, 'arc': {'interval': 100, 'frames': '◜◠◝◞◡◟'},
    'circle': {'interval': 120, 'frames': '◡⊙◠'}, 'squareCorners': {
    'interval': 180, 'frames': '◰◳◲◱'}, 'circleQuarters': {'interval': 120,
    'frames': '◴◷◶◵'}, 'circleHalves': {'interval': 50, 'frames': '◐◓◑◒'},
    'squish': {'interval': 100, 'frames': '╫╪'}, 'toggle': {'interval': 250,
    'frames': '⊶⊷'}, 'toggle2': {'interval': 80, 'frames': '▫▪'}, 'toggle3':
    {'interval': 120, 'frames': '□■'}, 'toggle4': {'interval': 100,
    'frames': '■□▪▫'}, 'toggle5': {'interval': 100, 'frames': '▮▯'},
    'toggle6': {'interval': 300, 'frames': 'ဝ၀'}, 'toggle7': {'interval': 
    80, 'frames': '⦾⦿'}, 'toggle8': {'interval': 100, 'frames': '◍◌'},
    'toggle9': {'interval': 100, 'frames': '◉◎'}, 'toggle10': {'interval': 
    100, 'frames': '㊂㊀㊁'}, 'toggle11': {'interval': 50, 'frames': '⧇⧆'},
    'toggle12': {'interval': 120, 'frames': '☗☖'}, 'toggle13': {'interval':
    80, 'frames': '=*-'}, 'arrow': {'interval': 100, 'frames': '←↖↑↗→↘↓↙'},
    'arrow2': {'interval': 80, 'frames': ['⬆️ ', '↗️ ', '➡️ ', '↘️ ', '⬇️ ',
    '↙️ ', '⬅️ ', '↖️ ']}, 'arrow3': {'interval': 120, 'frames': ['▹▹▹▹▹',
    '▸▹▹▹▹', '▹▸▹▹▹', '▹▹▸▹▹', '▹▹▹▸▹', '▹▹▹▹▸']}, 'bouncingBar': {
    'interval': 80, 'frames': ['[    ]', '[=   ]', '[==  ]', '[=== ]',
    '[ ===]', '[  ==]', '[   =]', '[    ]', '[   =]', '[  ==]', '[ ===]',
    '[====]', '[=== ]', '[==  ]', '[=   ]']}, 'bouncingBall': {'interval': 
    80, 'frames': ['( ●    )', '(  ●   )', '(   ●  )', '(    ● )',
    '(     ●)', '(    ● )', '(   ●  )', '(  ●   )', '( ●    )', '(●     )']
    }, 'smiley': {'interval': 200, 'frames': ['😄 ', '😝 ']}, 'monkey': {
    'interval': 300, 'frames': ['🙈 ', '🙈 ', '🙉 ', '🙊 ']}, 'hearts': {
    'interval': 100, 'frames': ['💛 ', '💙 ', '💜 ', '💚 ', '❤️ ']}, 'clock': {
    'interval': 100, 'frames': ['🕛 ', '🕐 ', '🕑 ', '🕒 ', '🕓 ', '🕔 ', '🕕 ',
    '🕖 ', '🕗 ', '🕘 ', '🕙 ', '🕚 ']}, 'earth': {'interval': 180, 'frames': [
    '🌍 ', '🌎 ', '🌏 ']}, 'material': {'interval': 17, 'frames': [
    '█▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁', '██▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁', '███▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁',
    '████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁', '██████▁▁▁▁▁▁▁▁▁▁▁▁▁▁', '██████▁▁▁▁▁▁▁▁▁▁▁▁▁▁',
    '███████▁▁▁▁▁▁▁▁▁▁▁▁▁', '████████▁▁▁▁▁▁▁▁▁▁▁▁', '█████████▁▁▁▁▁▁▁▁▁▁▁',
    '█████████▁▁▁▁▁▁▁▁▁▁▁', '██████████▁▁▁▁▁▁▁▁▁▁', '███████████▁▁▁▁▁▁▁▁▁',
    '█████████████▁▁▁▁▁▁▁', '██████████████▁▁▁▁▁▁', '██████████████▁▁▁▁▁▁',
    '▁██████████████▁▁▁▁▁', '▁██████████████▁▁▁▁▁', '▁██████████████▁▁▁▁▁',
    '▁▁██████████████▁▁▁▁', '▁▁▁██████████████▁▁▁', '▁▁▁▁█████████████▁▁▁',
    '▁▁▁▁██████████████▁▁', '▁▁▁▁██████████████▁▁', '▁▁▁▁▁██████████████▁',
    '▁▁▁▁▁██████████████▁', '▁▁▁▁▁██████████████▁', '▁▁▁▁▁▁██████████████',
    '▁▁▁▁▁▁██████████████', '▁▁▁▁▁▁▁█████████████', '▁▁▁▁▁▁▁█████████████',
    '▁▁▁▁▁▁▁▁████████████', '▁▁▁▁▁▁▁▁████████████', '▁▁▁▁▁▁▁▁▁███████████',
    '▁▁▁▁▁▁▁▁▁███████████', '▁▁▁▁▁▁▁▁▁▁██████████', '▁▁▁▁▁▁▁▁▁▁██████████',
    '▁▁▁▁▁▁▁▁▁▁▁▁████████', '▁▁▁▁▁▁▁▁▁▁▁▁▁███████', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁██████',
    '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████', '█▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████',
    '██▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁███', '██▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁███', '███▁▁▁▁▁▁▁▁▁▁▁▁▁▁███',
    '████▁▁▁▁▁▁▁▁▁▁▁▁▁▁██', '█████▁▁▁▁▁▁▁▁▁▁▁▁▁▁█', '█████▁▁▁▁▁▁▁▁▁▁▁▁▁▁█',
    '██████▁▁▁▁▁▁▁▁▁▁▁▁▁█', '████████▁▁▁▁▁▁▁▁▁▁▁▁', '█████████▁▁▁▁▁▁▁▁▁▁▁',
    '█████████▁▁▁▁▁▁▁▁▁▁▁', '█████████▁▁▁▁▁▁▁▁▁▁▁', '█████████▁▁▁▁▁▁▁▁▁▁▁',
    '███████████▁▁▁▁▁▁▁▁▁', '████████████▁▁▁▁▁▁▁▁', '████████████▁▁▁▁▁▁▁▁',
    '██████████████▁▁▁▁▁▁', '██████████████▁▁▁▁▁▁', '▁██████████████▁▁▁▁▁',
    '▁██████████████▁▁▁▁▁', '▁▁▁█████████████▁▁▁▁', '▁▁▁▁▁████████████▁▁▁',
    '▁▁▁▁▁████████████▁▁▁', '▁▁▁▁▁▁███████████▁▁▁', '▁▁▁▁▁▁▁▁█████████▁▁▁',
    '▁▁▁▁▁▁▁▁█████████▁▁▁', '▁▁▁▁▁▁▁▁▁█████████▁▁', '▁▁▁▁▁▁▁▁▁█████████▁▁',
    '▁▁▁▁▁▁▁▁▁▁█████████▁', '▁▁▁▁▁▁▁▁▁▁▁████████▁', '▁▁▁▁▁▁▁▁▁▁▁████████▁',
    '▁▁▁▁▁▁▁▁▁▁▁▁███████▁', '▁▁▁▁▁▁▁▁▁▁▁▁███████▁', '▁▁▁▁▁▁▁▁▁▁▁▁▁███████',
    '▁▁▁▁▁▁▁▁▁▁▁▁▁███████', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█████', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████',
    '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁███',
    '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁███', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁██', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁██',
    '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁██', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█',
    '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁',
    '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁', '▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁']}, 'moon': {'interval': 
    80, 'frames': ['🌑 ', '🌒 ', '🌓 ', '🌔 ', '🌕 ', '🌖 ', '🌗 ', '🌘 ']},
    'runner': {'interval': 140, 'frames': ['🚶 ', '🏃 ']}, 'pong': {
    'interval': 80, 'frames': ['▐⠂       ▌', '▐⠈       ▌', '▐ ⠂      ▌',
    '▐ ⠠      ▌', '▐  ⡀     ▌', '▐  ⠠     ▌', '▐   ⠂    ▌', '▐   ⠈    ▌',
    '▐    ⠂   ▌', '▐    ⠠   ▌', '▐     ⡀  ▌', '▐     ⠠  ▌', '▐      ⠂ ▌',
    '▐      ⠈ ▌', '▐       ⠂▌', '▐       ⠠▌', '▐       ⡀▌', '▐      ⠠ ▌',
    '▐      ⠂ ▌', '▐     ⠈  ▌', '▐     ⠂  ▌', '▐    ⠠   ▌', '▐    ⡀   ▌',
    '▐   ⠠    ▌', '▐   ⠂    ▌', '▐  ⠈     ▌', '▐  ⠂     ▌', '▐ ⠠      ▌',
    '▐ ⡀      ▌', '▐⠠       ▌']}, 'shark': {'interval': 120, 'frames': [
    '▐|\\____________▌', '▐_|\\___________▌', '▐__|\\__________▌',
    '▐___|\\_________▌', '▐____|\\________▌', '▐_____|\\_______▌',
    '▐______|\\______▌', '▐_______|\\_____▌', '▐________|\\____▌',
    '▐_________|\\___▌', '▐__________|\\__▌', '▐___________|\\_▌',
    '▐____________|\\▌', '▐____________/|▌', '▐___________/|_▌',
    '▐__________/|__▌', '▐_________/|___▌', '▐________/|____▌',
    '▐_______/|_____▌', '▐______/|______▌', '▐_____/|_______▌',
    '▐____/|________▌', '▐___/|_________▌', '▐__/|__________▌',
    '▐_/|___________▌', '▐/|____________▌']}, 'dqpb': {'interval': 100,
    'frames': 'dqpb'}, 'weather': {'interval': 100, 'frames': ['☀️ ', '☀️ ',
    '☀️ ', '🌤 ', '⛅️ ', '🌥 ', '☁️ ', '🌧 ', '🌨 ', '🌧 ', '🌨 ', '🌧 ', '🌨 ',
    '⛈ ', '🌨 ', '🌧 ', '🌨 ', '☁️ ', '🌥 ', '⛅️ ', '🌤 ', '☀️ ', '☀️ ']},
    'christmas': {'interval': 400, 'frames': '🌲🎄'}, 'grenade': {'interval':
    80, 'frames': ['،   ', '′   ', ' ´ ', ' ‾ ', '  ⸌', '  ⸊', '  |', '  ⁎',
    '  ⁕', ' ෴ ', '  ⁓', '   ', '   ', '   ']}, 'point': {'interval': 125,
    'frames': ['∙∙∙', '●∙∙', '∙●∙', '∙∙●', '∙∙∙']}, 'layer': {'interval': 
    150, 'frames': '-=≡'}, 'betaWave': {'interval': 80, 'frames': [
    'ρββββββ', 'βρβββββ', 'ββρββββ', 'βββρβββ', 'ββββρββ', 'βββββρβ',
    'ββββββρ']}, 'aesthetic': {'interval': 80, 'frames': ['▰▱▱▱▱▱▱',
    '▰▰▱▱▱▱▱', '▰▰▰▱▱▱▱', '▰▰▰▰▱▱▱', '▰▰▰▰▰▱▱', '▰▰▰▰▰▰▱', '▰▰▰▰▰▰▰',
    '▰▱▱▱▱▱▱']}}

DEFAULT_TERMINAL_THEME = TerminalTheme((255, 255, 255), (0, 0, 0), [(0, 0, 0), (128, 0, 0), (0, 128,
    0), (128, 128, 0), (0, 0, 128), (128, 0, 128), (0, 128, 128), (192, 192,
    192)], [(128, 128, 128), (255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 0,
    255), (255, 0, 255), (0, 255, 255), (255, 255, 255)])

MONOKAI = TerminalTheme((12, 12, 12), (217, 217, 217), [(26, 26, 26), (244, 0, 95), (
    152, 224, 36), (253, 151, 31), (157, 101, 255), (244, 0, 95), (88, 209,
    235), (196, 197, 181), (98, 94, 76)], [(244, 0, 95), (152, 224, 36), (
    224, 213, 97), (157, 101, 255), (244, 0, 95), (88, 209, 235), (246, 246,
    239)])

DIMMED_MONOKAI = TerminalTheme((25, 25, 25), (185, 188, 186), [(58, 61, 67), (190, 63, 72),
    (135, 154, 59), (197, 166, 53), (79, 118, 161), (133, 92, 141), (87, 
    143, 164), (185, 188, 186), (136, 137, 135)], [(251, 0, 31), (15, 114, 
    47), (196, 112, 51), (24, 109, 227), (251, 0, 103), (46, 112, 109), (
    253, 255, 185)])

NIGHT_OWLISH = TerminalTheme((255, 255, 255), (64, 63, 83), [(1, 22, 39), (211, 66, 62), (
    42, 162, 152), (218, 170, 1), (72, 118, 214), (64, 63, 83), (8, 145, 
    106), (122, 129, 129), (122, 129, 129)], [(247, 110, 110), (73, 208, 
    197), (218, 194, 107), (92, 167, 228), (105, 112, 152), (0, 201, 144),
    (152, 159, 177)])

SVG_EXPORT_THEME = TerminalTheme((41, 41, 41), (197, 200, 198), [(75, 78, 85), (204, 85, 90),
    (152, 168, 75), (208, 179, 68), (96, 138, 177), (152, 114, 159), (104, 
    160, 179), (197, 200, 198), (154, 155, 153)], [(255, 38, 39), (0, 130, 
    61), (208, 132, 66), (25, 132, 233), (255, 44, 122), (57, 130, 128), (
    253, 253, 197)])

BEGIN_BLOCK_ELEMENTS = ['█', '█', '█', '▐', '▐', '▐', '▕', '▕']

END_BLOCK_ELEMENTS = [' ', '▏', '▎', '▍', '▌', '▋', '▊', '▉']

FULL_BLOCK = """█"""

DEFAULT_THEME = """monokai"""

RICH_SYNTAX_THEMES = {'ansi_light': ANSI_LIGHT, 'ansi_dark': ANSI_DARK}

NUMBERS_COLUMN_DEFAULT_PADDING = (2)

CONSOLE_HTML_FORMAT = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
{stylesheet}
body {{
    color: {foreground};
    background-color: {background};
}}
</style>
</head>
<body>
    <pre style="font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace"><code style="font-family:inherit">{code}</code></pre>
</body>
</html>
"""

CONSOLE_SVG_FORMAT = """<svg class="rich-terminal" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
    <!-- Generated with Rich https://www.textualize.io -->
    <style>

    @font-face {{
        font-family: "Fira Code";
        src: local("FiraCode-Regular"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Regular.woff2") format("woff2"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Regular.woff") format("woff");
        font-style: normal;
        font-weight: 400;
    }}
    @font-face {{
        font-family: "Fira Code";
        src: local("FiraCode-Bold"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Bold.woff2") format("woff2"),
                url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Bold.woff") format("woff");
        font-style: bold;
        font-weight: 700;
    }}

    .{unique_id}-matrix {{
        font-family: Fira Code, monospace;
        font-size: {char_height}px;
        line-height: {line_height}px;
        font-variant-east-asian: full-width;
    }}

    .{unique_id}-title {{
        font-size: 18px;
        font-weight: bold;
        font-family: arial;
    }}

    {styles}
    </style>

    <defs>
    <clipPath id="{unique_id}-clip-terminal">
      <rect x="0" y="0" width="{terminal_width}" height="{terminal_height}" />
    </clipPath>
    {lines}
    </defs>

    {chrome}
    <g transform="translate({terminal_x}, {terminal_y})" clip-path="url(#{unique_id}-clip-terminal)">
    {backgrounds}
    <g class="{unique_id}-matrix">
    {matrix}
    </g>
    </g>
</svg>
"""

_SVG_FONT_FAMILY = """Rich Fira Code"""

_SVG_CLASSES_PREFIX = """rich-svg"""

PULSE_SIZE = (20)

BELL = (1)

CARRIAGE_RETURN = (2)

HOME = (3)

CLEAR = (4)

ENABLE_ALT_SCREEN = (7)

DISABLE_ALT_SCREEN = (8)

CURSOR_UP = (9)

CURSOR_DOWN = (10)

CURSOR_FORWARD = (11)

CURSOR_BACKWARD = (12)

CURSOR_MOVE_TO_COLUMN = (13)

CURSOR_MOVE_TO = (14)

ERASE_IN_LINE = (15)

SET_WINDOW_TITLE = (16)

SGR_STYLE_MAP = {(1): 'bold', (2): 'dim', (3): 'italic', (4): 'underline', (5): 'blink', (6
    ): 'blink2', (7): 'reverse', (8): 'conceal', (9): 'strike', (21):
    'underline2', (22): 'not dim not bold', (23): 'not italic', (24):
    'not underline', (25): 'not blink', (26): 'not blink2', (27):
    'not reverse', (28): 'not conceal', (29): 'not strike', (30):
    'color(0)', (31): 'color(1)', (32): 'color(2)', (33): 'color(3)', (34):
    'color(4)', (35): 'color(5)', (36): 'color(6)', (37): 'color(7)', (39):
    'default', (40): 'on color(0)', (41): 'on color(1)', (42):
    'on color(2)', (43): 'on color(3)', (44): 'on color(4)', (45):
    'on color(5)', (46): 'on color(6)', (47): 'on color(7)', (49):
    'on default', (51): 'frame', (52): 'encircle', (53): 'overline', (54):
    'not frame not encircle', (55): 'not overline', (90): 'color(8)', (91):
    'color(9)', (92): 'color(10)', (93): 'color(11)', (94): 'color(12)', (
    95): 'color(13)', (96): 'color(14)', (97): 'color(15)', (100):
    'on color(8)', (101): 'on color(9)', (102): 'on color(10)', (103):
    'on color(11)', (104): 'on color(12)', (105): 'on color(13)', (106):
    'on color(14)', (107): 'on color(15)'}

_I = typing.TypeVar('_I', TextIO, BinaryIO)

CELL_WIDTHS = [(0, 0, 0), (1, 31, -1), (127, 159, -1), (173, 173, 0), (768, 879, 0), (
    1155, 1161, 0), (1425, 1469, 0), (1471, 1471, 0), (1473, 1474, 0), (
    1476, 1477, 0), (1479, 1479, 0), (1536, 1541, 0), (1552, 1562, 0), (
    1564, 1564, 0), (1611, 1631, 0), (1648, 1648, 0), (1750, 1757, 0), (
    1759, 1764, 0), (1767, 1768, 0), (1770, 1773, 0), (1807, 1807, 0), (
    1809, 1809, 0), (1840, 1866, 0), (1958, 1968, 0), (2027, 2035, 0), (
    2045, 2045, 0), (2070, 2073, 0), (2075, 2083, 0), (2085, 2087, 0), (
    2089, 2093, 0), (2137, 2139, 0), (2192, 2193, 0), (2200, 2207, 0), (
    2250, 2307, 0), (2362, 2364, 0), (2366, 2383, 0), (2385, 2391, 0), (
    2402, 2403, 0), (2433, 2435, 0), (2492, 2492, 0), (2494, 2500, 0), (
    2503, 2504, 0), (2507, 2509, 0), (2519, 2519, 0), (2530, 2531, 0), (
    2558, 2558, 0), (2561, 2563, 0), (2620, 2620, 0), (2622, 2626, 0), (
    2631, 2632, 0), (2635, 2637, 0), (2641, 2641, 0), (2672, 2673, 0), (
    2677, 2677, 0), (2689, 2691, 0), (2748, 2748, 0), (2750, 2757, 0), (
    2759, 2761, 0), (2763, 2765, 0), (2786, 2787, 0), (2810, 2815, 0), (
    2817, 2819, 0), (2876, 2876, 0), (2878, 2884, 0), (2887, 2888, 0), (
    2891, 2893, 0), (2901, 2903, 0), (2914, 2915, 0), (2946, 2946, 0), (
    3006, 3010, 0), (3014, 3016, 0), (3018, 3021, 0), (3031, 3031, 0), (
    3072, 3076, 0), (3132, 3132, 0), (3134, 3140, 0), (3142, 3144, 0), (
    3146, 3149, 0), (3157, 3158, 0), (3170, 3171, 0), (3201, 3203, 0), (
    3260, 3260, 0), (3262, 3268, 0), (3270, 3272, 0), (3274, 3277, 0), (
    3285, 3286, 0), (3298, 3299, 0), (3315, 3315, 0), (3328, 3331, 0), (
    3387, 3388, 0), (3390, 3396, 0), (3398, 3400, 0), (3402, 3405, 0), (
    3415, 3415, 0), (3426, 3427, 0), (3457, 3459, 0), (3530, 3530, 0), (
    3535, 3540, 0), (3542, 3542, 0), (3544, 3551, 0), (3570, 3571, 0), (
    3633, 3633, 0), (3636, 3642, 0), (3655, 3662, 0), (3761, 3761, 0), (
    3764, 3772, 0), (3784, 3790, 0), (3864, 3865, 0), (3893, 3893, 0), (
    3895, 3895, 0), (3897, 3897, 0), (3902, 3903, 0), (3953, 3972, 0), (
    3974, 3975, 0), (3981, 3991, 0), (3993, 4028, 0), (4038, 4038, 0), (
    4139, 4158, 0), (4182, 4185, 0), (4190, 4192, 0), (4194, 4196, 0), (
    4199, 4205, 0), (4209, 4212, 0), (4226, 4237, 0), (4239, 4239, 0), (
    4250, 4253, 0), (4352, 4447, 2), (4448, 4607, 0), (4957, 4959, 0), (
    5906, 5909, 0), (5938, 5940, 0), (5970, 5971, 0), (6002, 6003, 0), (
    6068, 6099, 0), (6109, 6109, 0), (6155, 6159, 0), (6277, 6278, 0), (
    6313, 6313, 0), (6432, 6443, 0), (6448, 6459, 0), (6679, 6683, 0), (
    6741, 6750, 0), (6752, 6780, 0), (6783, 6783, 0), (6832, 6862, 0), (
    6912, 6916, 0), (6964, 6980, 0), (7019, 7027, 0), (7040, 7042, 0), (
    7073, 7085, 0), (7142, 7155, 0), (7204, 7223, 0), (7376, 7378, 0), (
    7380, 7400, 0), (7405, 7405, 0), (7412, 7412, 0), (7415, 7417, 0), (
    7616, 7679, 0), (8203, 8207, 0), (8232, 8238, 0), (8288, 8292, 0), (
    8294, 8303, 0), (8400, 8432, 0), (8986, 8987, 2), (9001, 9002, 2), (
    9193, 9196, 2), (9200, 9200, 2), (9203, 9203, 2), (9725, 9726, 2), (
    9748, 9749, 2), (9800, 9811, 2), (9855, 9855, 2), (9875, 9875, 2), (
    9889, 9889, 2), (9898, 9899, 2), (9917, 9918, 2), (9924, 9925, 2), (
    9934, 9934, 2), (9940, 9940, 2), (9962, 9962, 2), (9970, 9971, 2), (
    9973, 9973, 2), (9978, 9978, 2), (9981, 9981, 2), (9989, 9989, 2), (
    9994, 9995, 2), (10024, 10024, 2), (10060, 10060, 2), (10062, 10062, 2),
    (10067, 10069, 2), (10071, 10071, 2), (10133, 10135, 2), (10160, 10160,
    2), (10175, 10175, 2), (11035, 11036, 2), (11088, 11088, 2), (11093, 
    11093, 2), (11503, 11505, 0), (11647, 11647, 0), (11744, 11775, 0), (
    11904, 11929, 2), (11931, 12019, 2), (12032, 12245, 2), (12272, 12329, 
    2), (12330, 12335, 0), (12336, 12350, 2), (12353, 12438, 2), (12441, 
    12442, 0), (12443, 12543, 2), (12549, 12591, 2), (12593, 12686, 2), (
    12688, 12771, 2), (12783, 12830, 2), (12832, 12871, 2), (12880, 19903, 
    2), (19968, 42124, 2), (42128, 42182, 2), (42607, 42610, 0), (42612, 
    42621, 0), (42654, 42655, 0), (42736, 42737, 0), (43010, 43010, 0), (
    43014, 43014, 0), (43019, 43019, 0), (43043, 43047, 0), (43052, 43052, 
    0), (43136, 43137, 0), (43188, 43205, 0), (43232, 43249, 0), (43263, 
    43263, 0), (43302, 43309, 0), (43335, 43347, 0), (43360, 43388, 2), (
    43392, 43395, 0), (43443, 43456, 0), (43493, 43493, 0), (43561, 43574, 
    0), (43587, 43587, 0), (43596, 43597, 0), (43643, 43645, 0), (43696, 
    43696, 0), (43698, 43700, 0), (43703, 43704, 0), (43710, 43711, 0), (
    43713, 43713, 0), (43755, 43759, 0), (43765, 43766, 0), (44003, 44010, 
    0), (44012, 44013, 0), (44032, 55203, 2), (55216, 55295, 0), (63744, 
    64255, 2), (64286, 64286, 0), (65024, 65039, 0), (65040, 65049, 2), (
    65056, 65071, 0), (65072, 65106, 2), (65108, 65126, 2), (65128, 65131, 
    2), (65279, 65279, 0), (65281, 65376, 2), (65504, 65510, 2), (65529, 
    65531, 0), (66045, 66045, 0), (66272, 66272, 0), (66422, 66426, 0), (
    68097, 68099, 0), (68101, 68102, 0), (68108, 68111, 0), (68152, 68154, 
    0), (68159, 68159, 0), (68325, 68326, 0), (68900, 68903, 0), (69291, 
    69292, 0), (69373, 69375, 0), (69446, 69456, 0), (69506, 69509, 0), (
    69632, 69634, 0), (69688, 69702, 0), (69744, 69744, 0), (69747, 69748, 
    0), (69759, 69762, 0), (69808, 69818, 0), (69821, 69821, 0), (69826, 
    69826, 0), (69837, 69837, 0), (69888, 69890, 0), (69927, 69940, 0), (
    69957, 69958, 0), (70003, 70003, 0), (70016, 70018, 0), (70067, 70080, 
    0), (70089, 70092, 0), (70094, 70095, 0), (70188, 70199, 0), (70206, 
    70206, 0), (70209, 70209, 0), (70367, 70378, 0), (70400, 70403, 0), (
    70459, 70460, 0), (70462, 70468, 0), (70471, 70472, 0), (70475, 70477, 
    0), (70487, 70487, 0), (70498, 70499, 0), (70502, 70508, 0), (70512, 
    70516, 0), (70709, 70726, 0), (70750, 70750, 0), (70832, 70851, 0), (
    71087, 71093, 0), (71096, 71104, 0), (71132, 71133, 0), (71216, 71232, 
    0), (71339, 71351, 0), (71453, 71467, 0), (71724, 71738, 0), (71984, 
    71989, 0), (71991, 71992, 0), (71995, 71998, 0), (72000, 72000, 0), (
    72002, 72003, 0), (72145, 72151, 0), (72154, 72160, 0), (72164, 72164, 
    0), (72193, 72202, 0), (72243, 72249, 0), (72251, 72254, 0), (72263, 
    72263, 0), (72273, 72283, 0), (72330, 72345, 0), (72751, 72758, 0), (
    72760, 72767, 0), (72850, 72871, 0), (72873, 72886, 0), (73009, 73014, 
    0), (73018, 73018, 0), (73020, 73021, 0), (73023, 73029, 0), (73031, 
    73031, 0), (73098, 73102, 0), (73104, 73105, 0), (73107, 73111, 0), (
    73459, 73462, 0), (73472, 73473, 0), (73475, 73475, 0), (73524, 73530, 
    0), (73534, 73538, 0), (78896, 78912, 0), (78919, 78933, 0), (92912, 
    92916, 0), (92976, 92982, 0), (94031, 94031, 0), (94033, 94087, 0), (
    94095, 94098, 0), (94176, 94179, 2), (94180, 94180, 0), (94192, 94193, 
    0), (94208, 100343, 2), (100352, 101589, 2), (101632, 101640, 2), (
    110576, 110579, 2), (110581, 110587, 2), (110589, 110590, 2), (110592, 
    110882, 2), (110898, 110898, 2), (110928, 110930, 2), (110933, 110933, 
    2), (110948, 110951, 2), (110960, 111355, 2), (113821, 113822, 0), (
    113824, 113827, 0), (118528, 118573, 0), (118576, 118598, 0), (119141, 
    119145, 0), (119149, 119170, 0), (119173, 119179, 0), (119210, 119213, 
    0), (119362, 119364, 0), (121344, 121398, 0), (121403, 121452, 0), (
    121461, 121461, 0), (121476, 121476, 0), (121499, 121503, 0), (121505, 
    121519, 0), (122880, 122886, 0), (122888, 122904, 0), (122907, 122913, 
    0), (122915, 122916, 0), (122918, 122922, 0), (123023, 123023, 0), (
    123184, 123190, 0), (123566, 123566, 0), (123628, 123631, 0), (124140, 
    124143, 0), (125136, 125142, 0), (125252, 125258, 0), (126980, 126980, 
    2), (127183, 127183, 2), (127374, 127374, 2), (127377, 127386, 2), (
    127488, 127490, 2), (127504, 127547, 2), (127552, 127560, 2), (127568, 
    127569, 2), (127584, 127589, 2), (127744, 127776, 2), (127789, 127797, 
    2), (127799, 127868, 2), (127870, 127891, 2), (127904, 127946, 2), (
    127951, 127955, 2), (127968, 127984, 2), (127988, 127988, 2), (127992, 
    127994, 2), (127995, 127999, 0), (128000, 128062, 2), (128064, 128064, 
    2), (128066, 128252, 2), (128255, 128317, 2), (128331, 128334, 2), (
    128336, 128359, 2), (128378, 128378, 2), (128405, 128406, 2), (128420, 
    128420, 2), (128507, 128591, 2), (128640, 128709, 2), (128716, 128716, 
    2), (128720, 128722, 2), (128725, 128727, 2), (128732, 128735, 2), (
    128747, 128748, 2), (128756, 128764, 2), (128992, 129003, 2), (129008, 
    129008, 2), (129292, 129338, 2), (129340, 129349, 2), (129351, 129535, 
    2), (129648, 129660, 2), (129664, 129672, 2), (129680, 129725, 2), (
    129727, 129733, 2), (129742, 129755, 2), (129760, 129768, 2), (129776, 
    129784, 2), (131072, 196605, 2), (196608, 262141, 2), (917505, 917505, 
    0), (917536, 917631, 0), (917760, 917999, 0)]

STDOUT = (-11)

ENABLE_VIRTUAL_TERMINAL_PROCESSING = (4)

COORD = wintypes._COORD

BRIGHT_BIT = (8)

ANSI_TO_WINDOWS = [0, 4, 2, 6, 1, 5, 3, 7, 8, 12, 10, 14, 9, 13, 11, 15]

JUPYTER_HTML_FORMAT = """<pre style="white-space:pre;overflow-x:auto;line-height:normal;font-family:Menlo,'DejaVu Sans Mono',consolas,'Courier New',monospace">{code}</pre>
"""

_HTML5_REPLACEMENTS = {u'"': u'%22', u'\\': u'\\\\'}

SSL_KEYWORDS = ('key_file', 'cert_file', 'cert_reqs', 'ca_certs', 'ssl_version',
    'ca_cert_dir', 'ssl_context', 'key_password', 'server_hostname')

FIRST_MEMBER = (0)

OTHER_MEMBERS = (1)

SWALLOW_DATA = (2)

CONTENT_DECODERS = ['gzip', 'deflate']

REDIRECT_STATUSES = [301, 302, 303, 307, 308]

DECODER_ERROR_CLASSES = (IOError, zlib.error)

RECENT_DATE = datetime.date(2024, 1, 1)

_CONTAINS_CONTROL_CHAR_RE = re.compile("[^-!#$%&'*+.^_`|~0-9a-zA-Z]")

GENERIC_ERROR = """too many error responses"""

SPECIFIC_ERROR = """too many {status_code} error responses"""

SSL_BLOCKSIZE = (16384)

SKIP_HEADER = """@@@SKIP_HEADER@@@"""

SKIPPABLE_HEADERS = frozenset(['accept-encoding', 'host', 'user-agent'])

ACCEPT_ENCODING = """gzip,deflate"""

_FAILEDTELL = object()

DEFAULT_TIMEOUT = _GLOBAL_DEFAULT_TIMEOUT

HAS_SNI = (True)

IS_PYOPENSSL = (False)

IS_SECURETRANSPORT = (False)

ALPN_PROTOCOLS = ['http/1.1']

HASHFUNC_MAP = {length: getattr(hashlib, algorithm, None) for length, algorithm in ((32,
    'md5'), (40, 'sha1'), (64, 'sha256'))}

PROTOCOL_TLS_CLIENT = PROTOCOL_TLS

OP_NO_COMPRESSION = (131072)

OP_NO_TICKET = (16384)

DEFAULT_CIPHERS = """:""".join(['ECDHE+AESGCM', 'ECDHE+CHACHA20', 'DHE+AESGCM',
    'DHE+CHACHA20', 'ECDH+AESGCM', 'DH+AESGCM', 'ECDH+AES', 'DH+AES',
    'RSA+AESGCM', 'RSA+AES', '!aNULL', '!eNULL', '!MD5', '!DSS'])

DEFAULT_ALLOWED_METHODS = frozenset(['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'])

RETRY_AFTER_STATUS_CODES = frozenset([413, 429, 503])

DEFAULT_REMOVE_HEADERS_ON_REDIRECT = frozenset(['Cookie', 'Authorization', 'Proxy-Authorization'])

DEFAULT_BACKOFF_MAX = (120)

NORMALIZABLE_SCHEMES = ('http', 'https', None)

PERCENT_RE = re.compile('%[a-fA-F0-9]{2}')

URI_RE = re.compile(
    '^(?:([a-zA-Z][a-zA-Z0-9+.-]*):)?(?://([^\\\\/?#]*))?([^?#]*)(?:\\?([^#]*))?(?:#(.*))?$'
    , re.UNICODE | re.DOTALL)

IPV4_PAT = """(?:[0-9]{1,3}\\.){3}[0-9]{1,3}"""

HEX_PAT = """[0-9A-Fa-f]{1,4}"""

LS32_PAT = """(?:{hex}:{hex}|{ipv4})""".format(hex=HEX_PAT, ipv4=IPV4_PAT)

UNRESERVED_PAT = """ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._\\-~"""

IPV6_PAT = ('(?:' + '|'.join([(x % _subs) for x in _variations]) + ')')

ZONE_ID_PAT = ('(?:%25|%)(?:[' + UNRESERVED_PAT + ']|%[a-fA-F0-9]{2})+')

IPV6_ADDRZ_PAT = ('\\[' + IPV6_PAT + '(?:' + ZONE_ID_PAT + ')?\\]')

REG_NAME_PAT = """(?:[^\\[\\]%:/?#]|%[a-fA-F0-9]{2})*"""

TARGET_RE = re.compile('^(/[^?#]*)(?:\\?([^#]*))?(?:#.*)?$')

IPV4_RE = re.compile('^' + IPV4_PAT + '$')

IPV6_RE = re.compile('^' + IPV6_PAT + '$')

IPV6_ADDRZ_RE = re.compile('^' + IPV6_ADDRZ_PAT + '$')

BRACELESS_IPV6_ADDRZ_RE = re.compile('^' + IPV6_ADDRZ_PAT[2:-2] + '$')

ZONE_ID_RE = re.compile('(' + ZONE_ID_PAT + ')\\]$')

_HOST_PORT_PAT = ('^(%s|%s|%s)(?::0*?(|0|[1-9][0-9]{0,4}))?$' % (REG_NAME_PAT, IPV4_PAT,
    IPV6_ADDRZ_PAT))

_HOST_PORT_RE = re.compile(_HOST_PORT_PAT, re.UNICODE | re.DOTALL)

UNRESERVED_CHARS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-~')

SUB_DELIM_CHARS = set("!$&'()*+,;=")

USERINFO_CHARS = (UNRESERVED_CHARS | SUB_DELIM_CHARS | {':'})

PATH_CHARS = (USERINFO_CHARS | {'@', '/'})

QUERY_CHARS = (PATH_CHARS | {'?'})

HAS_IPV6 = _has_ipv6('::1')

SSL_WRITE_BLOCKSIZE = (16384)

CIPHER_SUITES = [SecurityConst.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384, SecurityConst.
    TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256, SecurityConst.
    TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384, SecurityConst.
    TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256, SecurityConst.
    TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256, SecurityConst.
    TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256, SecurityConst.
    TLS_DHE_RSA_WITH_AES_256_GCM_SHA384, SecurityConst.
    TLS_DHE_RSA_WITH_AES_128_GCM_SHA256, SecurityConst.
    TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384, SecurityConst.
    TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA, SecurityConst.
    TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256, SecurityConst.
    TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA, SecurityConst.
    TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384, SecurityConst.
    TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA, SecurityConst.
    TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256, SecurityConst.
    TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA, SecurityConst.
    TLS_DHE_RSA_WITH_AES_256_CBC_SHA256, SecurityConst.
    TLS_DHE_RSA_WITH_AES_256_CBC_SHA, SecurityConst.
    TLS_DHE_RSA_WITH_AES_128_CBC_SHA256, SecurityConst.
    TLS_DHE_RSA_WITH_AES_128_CBC_SHA, SecurityConst.TLS_AES_256_GCM_SHA384,
    SecurityConst.TLS_AES_128_GCM_SHA256, SecurityConst.
    TLS_RSA_WITH_AES_256_GCM_SHA384, SecurityConst.
    TLS_RSA_WITH_AES_128_GCM_SHA256, SecurityConst.TLS_AES_128_CCM_8_SHA256,
    SecurityConst.TLS_AES_128_CCM_SHA256, SecurityConst.
    TLS_RSA_WITH_AES_256_CBC_SHA256, SecurityConst.
    TLS_RSA_WITH_AES_128_CBC_SHA256, SecurityConst.
    TLS_RSA_WITH_AES_256_CBC_SHA, SecurityConst.TLS_RSA_WITH_AES_128_CBC_SHA]

_PEM_CERTS_RE = re.compile(b'-----BEGIN CERTIFICATE-----\n(.*?)\n-----END CERTIFICATE-----',
    re.DOTALL)

TLS_PROTOCOL_VERSIONS = {'SSLv2': (0, 2), 'SSLv3': (3, 0), 'TLSv1': (3, 1), 'TLSv1.1': (3, 2),
    'TLSv1.2': (3, 3)}

TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384 = (49196)

TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384 = (49200)

TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256 = (49195)

TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 = (49199)

TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256 = (52393)

TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256 = (52392)

TLS_DHE_RSA_WITH_AES_256_GCM_SHA384 = (159)

TLS_DHE_RSA_WITH_AES_128_GCM_SHA256 = (158)

TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA384 = (49188)

TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA384 = (49192)

TLS_ECDHE_ECDSA_WITH_AES_256_CBC_SHA = (49162)

TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA = (49172)

TLS_DHE_RSA_WITH_AES_256_CBC_SHA256 = (107)

TLS_DHE_RSA_WITH_AES_256_CBC_SHA = (57)

TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA256 = (49187)

TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA256 = (49191)

TLS_ECDHE_ECDSA_WITH_AES_128_CBC_SHA = (49161)

TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA = (49171)

TLS_DHE_RSA_WITH_AES_128_CBC_SHA256 = (103)

TLS_DHE_RSA_WITH_AES_128_CBC_SHA = (51)

TLS_RSA_WITH_AES_256_GCM_SHA384 = (157)

TLS_RSA_WITH_AES_128_GCM_SHA256 = (156)

TLS_RSA_WITH_AES_256_CBC_SHA256 = (61)

TLS_RSA_WITH_AES_128_CBC_SHA256 = (60)

TLS_RSA_WITH_AES_256_CBC_SHA = (53)

TLS_RSA_WITH_AES_128_CBC_SHA = (47)

TLS_AES_128_GCM_SHA256 = (4865)

TLS_AES_256_GCM_SHA384 = (4866)

TLS_AES_128_CCM_8_SHA256 = (4869)

TLS_AES_128_CCM_SHA256 = (4868)

WRITE_SUPPORT = (False)

_PEP440_FALLBACK = re.compile('^v?(?P<safe>(?:[0-9]+!)?[0-9]+(?:\\.[0-9]+)*)', re.I)

PY_MAJOR = f"""{sys.version_info.major}.{sys.version_info.minor}"""

EGG_DIST = (3)

BINARY_DIST = (2)

SOURCE_DIST = (1)

CHECKOUT_DIST = (0)

DEVELOP_DIST = (-1)

MODULE = re.compile('\\w+(\\.\\w+)*$').match

EGG_NAME = re.compile(
    """
    (?P<name>[^-]+) (
        -(?P<ver>[^-]+) (
            -py(?P<pyver>[^-]+) (
                -(?P<plat>.+)
            )?
        )?
    )?
    """
    , re.VERBOSE | re.IGNORECASE).match

PKG_INFO = """METADATA"""

EQEQ = re.compile('([\\(,])\\s*(\\d.*?)\\s*([,\\)])')

_LOCALE_ENCODING = ('locale' if sys.version_info >= (3, 10) else None)

PROPS = ('user_data_dir', 'user_config_dir', 'user_cache_dir', 'user_state_dir',
    'user_log_dir', 'user_documents_dir', 'user_downloads_dir',
    'user_pictures_dir', 'user_videos_dir', 'user_music_dir',
    'user_runtime_dir', 'site_data_dir', 'site_config_dir',
    'site_cache_dir', 'site_runtime_dir')

TOOLS = fitz.Tools()

FZ_VERSION = _fitz.FZ_VERSION

FZ_VERSION_MAJOR = _fitz.FZ_VERSION_MAJOR

FZ_VERSION_MINOR = _fitz.FZ_VERSION_MINOR

FZ_VERSION_PATCH = _fitz.FZ_VERSION_PATCH

TESSDATA_PREFIX = os.getenv('TESSDATA_PREFIX')

PDF_ANNOT_TEXT = _fitz.PDF_ANNOT_TEXT

PDF_ANNOT_LINK = _fitz.PDF_ANNOT_LINK

PDF_ANNOT_FREE_TEXT = _fitz.PDF_ANNOT_FREE_TEXT

PDF_ANNOT_LINE = _fitz.PDF_ANNOT_LINE

PDF_ANNOT_SQUARE = _fitz.PDF_ANNOT_SQUARE

PDF_ANNOT_CIRCLE = _fitz.PDF_ANNOT_CIRCLE

PDF_ANNOT_POLYGON = _fitz.PDF_ANNOT_POLYGON

PDF_ANNOT_POLY_LINE = _fitz.PDF_ANNOT_POLY_LINE

PDF_ANNOT_HIGHLIGHT = _fitz.PDF_ANNOT_HIGHLIGHT

PDF_ANNOT_UNDERLINE = _fitz.PDF_ANNOT_UNDERLINE

PDF_ANNOT_SQUIGGLY = _fitz.PDF_ANNOT_SQUIGGLY

PDF_ANNOT_STRIKE_OUT = _fitz.PDF_ANNOT_STRIKE_OUT

PDF_ANNOT_REDACT = _fitz.PDF_ANNOT_REDACT

PDF_ANNOT_STAMP = _fitz.PDF_ANNOT_STAMP

PDF_ANNOT_CARET = _fitz.PDF_ANNOT_CARET

PDF_ANNOT_INK = _fitz.PDF_ANNOT_INK

PDF_ANNOT_POPUP = _fitz.PDF_ANNOT_POPUP

PDF_ANNOT_FILE_ATTACHMENT = _fitz.PDF_ANNOT_FILE_ATTACHMENT

PDF_ANNOT_SOUND = _fitz.PDF_ANNOT_SOUND

PDF_ANNOT_MOVIE = _fitz.PDF_ANNOT_MOVIE

PDF_ANNOT_RICH_MEDIA = _fitz.PDF_ANNOT_RICH_MEDIA

PDF_ANNOT_WIDGET = _fitz.PDF_ANNOT_WIDGET

PDF_ANNOT_SCREEN = _fitz.PDF_ANNOT_SCREEN

PDF_ANNOT_PRINTER_MARK = _fitz.PDF_ANNOT_PRINTER_MARK

PDF_ANNOT_TRAP_NET = _fitz.PDF_ANNOT_TRAP_NET

PDF_ANNOT_WATERMARK = _fitz.PDF_ANNOT_WATERMARK

PDF_ANNOT_3D = _fitz.PDF_ANNOT_3D

PDF_ANNOT_PROJECTION = _fitz.PDF_ANNOT_PROJECTION

PDF_ANNOT_UNKNOWN = _fitz.PDF_ANNOT_UNKNOWN

PDF_REDACT_IMAGE_NONE = _fitz.PDF_REDACT_IMAGE_NONE

PDF_REDACT_IMAGE_REMOVE = _fitz.PDF_REDACT_IMAGE_REMOVE

PDF_REDACT_IMAGE_PIXELS = _fitz.PDF_REDACT_IMAGE_PIXELS

PDF_ANNOT_IS_INVISIBLE = _fitz.PDF_ANNOT_IS_INVISIBLE

PDF_ANNOT_IS_HIDDEN = _fitz.PDF_ANNOT_IS_HIDDEN

PDF_ANNOT_IS_PRINT = _fitz.PDF_ANNOT_IS_PRINT

PDF_ANNOT_IS_NO_ZOOM = _fitz.PDF_ANNOT_IS_NO_ZOOM

PDF_ANNOT_IS_NO_ROTATE = _fitz.PDF_ANNOT_IS_NO_ROTATE

PDF_ANNOT_IS_NO_VIEW = _fitz.PDF_ANNOT_IS_NO_VIEW

PDF_ANNOT_IS_READ_ONLY = _fitz.PDF_ANNOT_IS_READ_ONLY

PDF_ANNOT_IS_LOCKED = _fitz.PDF_ANNOT_IS_LOCKED

PDF_ANNOT_IS_TOGGLE_NO_VIEW = _fitz.PDF_ANNOT_IS_TOGGLE_NO_VIEW

PDF_ANNOT_IS_LOCKED_CONTENTS = _fitz.PDF_ANNOT_IS_LOCKED_CONTENTS

PDF_ANNOT_LE_NONE = _fitz.PDF_ANNOT_LE_NONE

PDF_ANNOT_LE_SQUARE = _fitz.PDF_ANNOT_LE_SQUARE

PDF_ANNOT_LE_CIRCLE = _fitz.PDF_ANNOT_LE_CIRCLE

PDF_ANNOT_LE_DIAMOND = _fitz.PDF_ANNOT_LE_DIAMOND

PDF_ANNOT_LE_OPEN_ARROW = _fitz.PDF_ANNOT_LE_OPEN_ARROW

PDF_ANNOT_LE_CLOSED_ARROW = _fitz.PDF_ANNOT_LE_CLOSED_ARROW

PDF_ANNOT_LE_BUTT = _fitz.PDF_ANNOT_LE_BUTT

PDF_ANNOT_LE_R_OPEN_ARROW = _fitz.PDF_ANNOT_LE_R_OPEN_ARROW

PDF_ANNOT_LE_R_CLOSED_ARROW = _fitz.PDF_ANNOT_LE_R_CLOSED_ARROW

PDF_ANNOT_LE_SLASH = _fitz.PDF_ANNOT_LE_SLASH

PDF_WIDGET_TYPE_UNKNOWN = _fitz.PDF_WIDGET_TYPE_UNKNOWN

PDF_WIDGET_TYPE_BUTTON = _fitz.PDF_WIDGET_TYPE_BUTTON

PDF_WIDGET_TYPE_CHECKBOX = _fitz.PDF_WIDGET_TYPE_CHECKBOX

PDF_WIDGET_TYPE_COMBOBOX = _fitz.PDF_WIDGET_TYPE_COMBOBOX

PDF_WIDGET_TYPE_LISTBOX = _fitz.PDF_WIDGET_TYPE_LISTBOX

PDF_WIDGET_TYPE_RADIOBUTTON = _fitz.PDF_WIDGET_TYPE_RADIOBUTTON

PDF_WIDGET_TYPE_SIGNATURE = _fitz.PDF_WIDGET_TYPE_SIGNATURE

PDF_WIDGET_TYPE_TEXT = _fitz.PDF_WIDGET_TYPE_TEXT

PDF_WIDGET_TX_FORMAT_NONE = _fitz.PDF_WIDGET_TX_FORMAT_NONE

PDF_WIDGET_TX_FORMAT_NUMBER = _fitz.PDF_WIDGET_TX_FORMAT_NUMBER

PDF_WIDGET_TX_FORMAT_SPECIAL = _fitz.PDF_WIDGET_TX_FORMAT_SPECIAL

PDF_WIDGET_TX_FORMAT_DATE = _fitz.PDF_WIDGET_TX_FORMAT_DATE

PDF_WIDGET_TX_FORMAT_TIME = _fitz.PDF_WIDGET_TX_FORMAT_TIME

PDF_FIELD_IS_READ_ONLY = _fitz.PDF_FIELD_IS_READ_ONLY

PDF_FIELD_IS_REQUIRED = _fitz.PDF_FIELD_IS_REQUIRED

PDF_FIELD_IS_NO_EXPORT = _fitz.PDF_FIELD_IS_NO_EXPORT

PDF_TX_FIELD_IS_MULTILINE = _fitz.PDF_TX_FIELD_IS_MULTILINE

PDF_TX_FIELD_IS_PASSWORD = _fitz.PDF_TX_FIELD_IS_PASSWORD

PDF_TX_FIELD_IS_FILE_SELECT = _fitz.PDF_TX_FIELD_IS_FILE_SELECT

PDF_TX_FIELD_IS_DO_NOT_SPELL_CHECK = _fitz.PDF_TX_FIELD_IS_DO_NOT_SPELL_CHECK

PDF_TX_FIELD_IS_DO_NOT_SCROLL = _fitz.PDF_TX_FIELD_IS_DO_NOT_SCROLL

PDF_TX_FIELD_IS_COMB = _fitz.PDF_TX_FIELD_IS_COMB

PDF_TX_FIELD_IS_RICH_TEXT = _fitz.PDF_TX_FIELD_IS_RICH_TEXT

PDF_BTN_FIELD_IS_NO_TOGGLE_TO_OFF = _fitz.PDF_BTN_FIELD_IS_NO_TOGGLE_TO_OFF

PDF_BTN_FIELD_IS_RADIO = _fitz.PDF_BTN_FIELD_IS_RADIO

PDF_BTN_FIELD_IS_PUSHBUTTON = _fitz.PDF_BTN_FIELD_IS_PUSHBUTTON

PDF_BTN_FIELD_IS_RADIOS_IN_UNISON = _fitz.PDF_BTN_FIELD_IS_RADIOS_IN_UNISON

PDF_CH_FIELD_IS_COMBO = _fitz.PDF_CH_FIELD_IS_COMBO

PDF_CH_FIELD_IS_EDIT = _fitz.PDF_CH_FIELD_IS_EDIT

PDF_CH_FIELD_IS_SORT = _fitz.PDF_CH_FIELD_IS_SORT

PDF_CH_FIELD_IS_MULTI_SELECT = _fitz.PDF_CH_FIELD_IS_MULTI_SELECT

PDF_CH_FIELD_IS_DO_NOT_SPELL_CHECK = _fitz.PDF_CH_FIELD_IS_DO_NOT_SPELL_CHECK

PDF_CH_FIELD_IS_COMMIT_ON_SEL_CHANGE = _fitz.PDF_CH_FIELD_IS_COMMIT_ON_SEL_CHANGE

PDF_SIGNATURE_ERROR_OKAY = _fitz.PDF_SIGNATURE_ERROR_OKAY

PDF_SIGNATURE_ERROR_NO_SIGNATURES = _fitz.PDF_SIGNATURE_ERROR_NO_SIGNATURES

PDF_SIGNATURE_ERROR_NO_CERTIFICATE = _fitz.PDF_SIGNATURE_ERROR_NO_CERTIFICATE

PDF_SIGNATURE_ERROR_DIGEST_FAILURE = _fitz.PDF_SIGNATURE_ERROR_DIGEST_FAILURE

PDF_SIGNATURE_ERROR_SELF_SIGNED = _fitz.PDF_SIGNATURE_ERROR_SELF_SIGNED

PDF_SIGNATURE_ERROR_SELF_SIGNED_IN_CHAIN = _fitz.PDF_SIGNATURE_ERROR_SELF_SIGNED_IN_CHAIN

PDF_SIGNATURE_ERROR_NOT_TRUSTED = _fitz.PDF_SIGNATURE_ERROR_NOT_TRUSTED

PDF_SIGNATURE_ERROR_UNKNOWN = _fitz.PDF_SIGNATURE_ERROR_UNKNOWN

PDF_SIGNATURE_SHOW_LABELS = _fitz.PDF_SIGNATURE_SHOW_LABELS

PDF_SIGNATURE_SHOW_DN = _fitz.PDF_SIGNATURE_SHOW_DN

PDF_SIGNATURE_SHOW_DATE = _fitz.PDF_SIGNATURE_SHOW_DATE

PDF_SIGNATURE_SHOW_TEXT_NAME = _fitz.PDF_SIGNATURE_SHOW_TEXT_NAME

PDF_SIGNATURE_SHOW_GRAPHIC_NAME = _fitz.PDF_SIGNATURE_SHOW_GRAPHIC_NAME

PDF_SIGNATURE_SHOW_LOGO = _fitz.PDF_SIGNATURE_SHOW_LOGO

PDF_SIGNATURE_DEFAULT_APPEARANCE = _fitz.PDF_SIGNATURE_DEFAULT_APPEARANCE

CS_RGB = _fitz.CS_RGB

CS_GRAY = _fitz.CS_GRAY

CS_CMYK = _fitz.CS_CMYK

PDF_ENCRYPT_KEEP = _fitz.PDF_ENCRYPT_KEEP

PDF_ENCRYPT_NONE = _fitz.PDF_ENCRYPT_NONE

PDF_ENCRYPT_RC4_40 = _fitz.PDF_ENCRYPT_RC4_40

PDF_ENCRYPT_RC4_128 = _fitz.PDF_ENCRYPT_RC4_128

PDF_ENCRYPT_AES_128 = _fitz.PDF_ENCRYPT_AES_128

PDF_ENCRYPT_AES_256 = _fitz.PDF_ENCRYPT_AES_256

PDF_ENCRYPT_UNKNOWN = _fitz.PDF_ENCRYPT_UNKNOWN

PDF_PERM_PRINT = _fitz.PDF_PERM_PRINT

PDF_PERM_MODIFY = _fitz.PDF_PERM_MODIFY

PDF_PERM_COPY = _fitz.PDF_PERM_COPY

PDF_PERM_ANNOTATE = _fitz.PDF_PERM_ANNOTATE

PDF_PERM_FORM = _fitz.PDF_PERM_FORM

PDF_PERM_ACCESSIBILITY = _fitz.PDF_PERM_ACCESSIBILITY

PDF_PERM_ASSEMBLE = _fitz.PDF_PERM_ASSEMBLE

PDF_PERM_PRINT_HQ = _fitz.PDF_PERM_PRINT_HQ

TEXT_FONT_SUPERSCRIPT = _fitz.TEXT_FONT_SUPERSCRIPT

TEXT_FONT_ITALIC = _fitz.TEXT_FONT_ITALIC

TEXT_FONT_SERIFED = _fitz.TEXT_FONT_SERIFED

TEXT_FONT_MONOSPACED = _fitz.TEXT_FONT_MONOSPACED

TEXT_FONT_BOLD = _fitz.TEXT_FONT_BOLD

UCDN_SCRIPT_COMMON = _fitz.UCDN_SCRIPT_COMMON

UCDN_SCRIPT_LATIN = _fitz.UCDN_SCRIPT_LATIN

UCDN_SCRIPT_GREEK = _fitz.UCDN_SCRIPT_GREEK

UCDN_SCRIPT_CYRILLIC = _fitz.UCDN_SCRIPT_CYRILLIC

UCDN_SCRIPT_ARMENIAN = _fitz.UCDN_SCRIPT_ARMENIAN

UCDN_SCRIPT_HEBREW = _fitz.UCDN_SCRIPT_HEBREW

UCDN_SCRIPT_ARABIC = _fitz.UCDN_SCRIPT_ARABIC

UCDN_SCRIPT_SYRIAC = _fitz.UCDN_SCRIPT_SYRIAC

UCDN_SCRIPT_THAANA = _fitz.UCDN_SCRIPT_THAANA

UCDN_SCRIPT_DEVANAGARI = _fitz.UCDN_SCRIPT_DEVANAGARI

UCDN_SCRIPT_BENGALI = _fitz.UCDN_SCRIPT_BENGALI

UCDN_SCRIPT_GURMUKHI = _fitz.UCDN_SCRIPT_GURMUKHI

UCDN_SCRIPT_GUJARATI = _fitz.UCDN_SCRIPT_GUJARATI

UCDN_SCRIPT_ORIYA = _fitz.UCDN_SCRIPT_ORIYA

UCDN_SCRIPT_TAMIL = _fitz.UCDN_SCRIPT_TAMIL

UCDN_SCRIPT_TELUGU = _fitz.UCDN_SCRIPT_TELUGU

UCDN_SCRIPT_KANNADA = _fitz.UCDN_SCRIPT_KANNADA

UCDN_SCRIPT_MALAYALAM = _fitz.UCDN_SCRIPT_MALAYALAM

UCDN_SCRIPT_SINHALA = _fitz.UCDN_SCRIPT_SINHALA

UCDN_SCRIPT_THAI = _fitz.UCDN_SCRIPT_THAI

UCDN_SCRIPT_LAO = _fitz.UCDN_SCRIPT_LAO

UCDN_SCRIPT_TIBETAN = _fitz.UCDN_SCRIPT_TIBETAN

UCDN_SCRIPT_MYANMAR = _fitz.UCDN_SCRIPT_MYANMAR

UCDN_SCRIPT_GEORGIAN = _fitz.UCDN_SCRIPT_GEORGIAN

UCDN_SCRIPT_HANGUL = _fitz.UCDN_SCRIPT_HANGUL

UCDN_SCRIPT_ETHIOPIC = _fitz.UCDN_SCRIPT_ETHIOPIC

UCDN_SCRIPT_CHEROKEE = _fitz.UCDN_SCRIPT_CHEROKEE

UCDN_SCRIPT_CANADIAN_ABORIGINAL = _fitz.UCDN_SCRIPT_CANADIAN_ABORIGINAL

UCDN_SCRIPT_OGHAM = _fitz.UCDN_SCRIPT_OGHAM

UCDN_SCRIPT_RUNIC = _fitz.UCDN_SCRIPT_RUNIC

UCDN_SCRIPT_KHMER = _fitz.UCDN_SCRIPT_KHMER

UCDN_SCRIPT_MONGOLIAN = _fitz.UCDN_SCRIPT_MONGOLIAN

UCDN_SCRIPT_HIRAGANA = _fitz.UCDN_SCRIPT_HIRAGANA

UCDN_SCRIPT_KATAKANA = _fitz.UCDN_SCRIPT_KATAKANA

UCDN_SCRIPT_BOPOMOFO = _fitz.UCDN_SCRIPT_BOPOMOFO

UCDN_SCRIPT_HAN = _fitz.UCDN_SCRIPT_HAN

UCDN_SCRIPT_YI = _fitz.UCDN_SCRIPT_YI

UCDN_SCRIPT_OLD_ITALIC = _fitz.UCDN_SCRIPT_OLD_ITALIC

UCDN_SCRIPT_GOTHIC = _fitz.UCDN_SCRIPT_GOTHIC

UCDN_SCRIPT_DESERET = _fitz.UCDN_SCRIPT_DESERET

UCDN_SCRIPT_INHERITED = _fitz.UCDN_SCRIPT_INHERITED

UCDN_SCRIPT_TAGALOG = _fitz.UCDN_SCRIPT_TAGALOG

UCDN_SCRIPT_HANUNOO = _fitz.UCDN_SCRIPT_HANUNOO

UCDN_SCRIPT_BUHID = _fitz.UCDN_SCRIPT_BUHID

UCDN_SCRIPT_TAGBANWA = _fitz.UCDN_SCRIPT_TAGBANWA

UCDN_SCRIPT_LIMBU = _fitz.UCDN_SCRIPT_LIMBU

UCDN_SCRIPT_TAI_LE = _fitz.UCDN_SCRIPT_TAI_LE

UCDN_SCRIPT_LINEAR_B = _fitz.UCDN_SCRIPT_LINEAR_B

UCDN_SCRIPT_UGARITIC = _fitz.UCDN_SCRIPT_UGARITIC

UCDN_SCRIPT_SHAVIAN = _fitz.UCDN_SCRIPT_SHAVIAN

UCDN_SCRIPT_OSMANYA = _fitz.UCDN_SCRIPT_OSMANYA

UCDN_SCRIPT_CYPRIOT = _fitz.UCDN_SCRIPT_CYPRIOT

UCDN_SCRIPT_BRAILLE = _fitz.UCDN_SCRIPT_BRAILLE

UCDN_SCRIPT_BUGINESE = _fitz.UCDN_SCRIPT_BUGINESE

UCDN_SCRIPT_COPTIC = _fitz.UCDN_SCRIPT_COPTIC

UCDN_SCRIPT_NEW_TAI_LUE = _fitz.UCDN_SCRIPT_NEW_TAI_LUE

UCDN_SCRIPT_GLAGOLITIC = _fitz.UCDN_SCRIPT_GLAGOLITIC

UCDN_SCRIPT_TIFINAGH = _fitz.UCDN_SCRIPT_TIFINAGH

UCDN_SCRIPT_SYLOTI_NAGRI = _fitz.UCDN_SCRIPT_SYLOTI_NAGRI

UCDN_SCRIPT_OLD_PERSIAN = _fitz.UCDN_SCRIPT_OLD_PERSIAN

UCDN_SCRIPT_KHAROSHTHI = _fitz.UCDN_SCRIPT_KHAROSHTHI

UCDN_SCRIPT_BALINESE = _fitz.UCDN_SCRIPT_BALINESE

UCDN_SCRIPT_CUNEIFORM = _fitz.UCDN_SCRIPT_CUNEIFORM

UCDN_SCRIPT_PHOENICIAN = _fitz.UCDN_SCRIPT_PHOENICIAN

UCDN_SCRIPT_PHAGS_PA = _fitz.UCDN_SCRIPT_PHAGS_PA

UCDN_SCRIPT_NKO = _fitz.UCDN_SCRIPT_NKO

UCDN_SCRIPT_SUNDANESE = _fitz.UCDN_SCRIPT_SUNDANESE

UCDN_SCRIPT_LEPCHA = _fitz.UCDN_SCRIPT_LEPCHA

UCDN_SCRIPT_OL_CHIKI = _fitz.UCDN_SCRIPT_OL_CHIKI

UCDN_SCRIPT_VAI = _fitz.UCDN_SCRIPT_VAI

UCDN_SCRIPT_SAURASHTRA = _fitz.UCDN_SCRIPT_SAURASHTRA

UCDN_SCRIPT_KAYAH_LI = _fitz.UCDN_SCRIPT_KAYAH_LI

UCDN_SCRIPT_REJANG = _fitz.UCDN_SCRIPT_REJANG

UCDN_SCRIPT_LYCIAN = _fitz.UCDN_SCRIPT_LYCIAN

UCDN_SCRIPT_CARIAN = _fitz.UCDN_SCRIPT_CARIAN

UCDN_SCRIPT_LYDIAN = _fitz.UCDN_SCRIPT_LYDIAN

UCDN_SCRIPT_CHAM = _fitz.UCDN_SCRIPT_CHAM

UCDN_SCRIPT_TAI_THAM = _fitz.UCDN_SCRIPT_TAI_THAM

UCDN_SCRIPT_TAI_VIET = _fitz.UCDN_SCRIPT_TAI_VIET

UCDN_SCRIPT_AVESTAN = _fitz.UCDN_SCRIPT_AVESTAN

UCDN_SCRIPT_EGYPTIAN_HIEROGLYPHS = _fitz.UCDN_SCRIPT_EGYPTIAN_HIEROGLYPHS

UCDN_SCRIPT_SAMARITAN = _fitz.UCDN_SCRIPT_SAMARITAN

UCDN_SCRIPT_LISU = _fitz.UCDN_SCRIPT_LISU

UCDN_SCRIPT_BAMUM = _fitz.UCDN_SCRIPT_BAMUM

UCDN_SCRIPT_JAVANESE = _fitz.UCDN_SCRIPT_JAVANESE

UCDN_SCRIPT_MEETEI_MAYEK = _fitz.UCDN_SCRIPT_MEETEI_MAYEK

UCDN_SCRIPT_IMPERIAL_ARAMAIC = _fitz.UCDN_SCRIPT_IMPERIAL_ARAMAIC

UCDN_SCRIPT_OLD_SOUTH_ARABIAN = _fitz.UCDN_SCRIPT_OLD_SOUTH_ARABIAN

UCDN_SCRIPT_INSCRIPTIONAL_PARTHIAN = _fitz.UCDN_SCRIPT_INSCRIPTIONAL_PARTHIAN

UCDN_SCRIPT_INSCRIPTIONAL_PAHLAVI = _fitz.UCDN_SCRIPT_INSCRIPTIONAL_PAHLAVI

UCDN_SCRIPT_OLD_TURKIC = _fitz.UCDN_SCRIPT_OLD_TURKIC

UCDN_SCRIPT_KAITHI = _fitz.UCDN_SCRIPT_KAITHI

UCDN_SCRIPT_BATAK = _fitz.UCDN_SCRIPT_BATAK

UCDN_SCRIPT_BRAHMI = _fitz.UCDN_SCRIPT_BRAHMI

UCDN_SCRIPT_MANDAIC = _fitz.UCDN_SCRIPT_MANDAIC

UCDN_SCRIPT_CHAKMA = _fitz.UCDN_SCRIPT_CHAKMA

UCDN_SCRIPT_MEROITIC_CURSIVE = _fitz.UCDN_SCRIPT_MEROITIC_CURSIVE

UCDN_SCRIPT_MEROITIC_HIEROGLYPHS = _fitz.UCDN_SCRIPT_MEROITIC_HIEROGLYPHS

UCDN_SCRIPT_MIAO = _fitz.UCDN_SCRIPT_MIAO

UCDN_SCRIPT_SHARADA = _fitz.UCDN_SCRIPT_SHARADA

UCDN_SCRIPT_SORA_SOMPENG = _fitz.UCDN_SCRIPT_SORA_SOMPENG

UCDN_SCRIPT_TAKRI = _fitz.UCDN_SCRIPT_TAKRI

UCDN_SCRIPT_UNKNOWN = _fitz.UCDN_SCRIPT_UNKNOWN

UCDN_SCRIPT_BASSA_VAH = _fitz.UCDN_SCRIPT_BASSA_VAH

UCDN_SCRIPT_CAUCASIAN_ALBANIAN = _fitz.UCDN_SCRIPT_CAUCASIAN_ALBANIAN

UCDN_SCRIPT_DUPLOYAN = _fitz.UCDN_SCRIPT_DUPLOYAN

UCDN_SCRIPT_ELBASAN = _fitz.UCDN_SCRIPT_ELBASAN

UCDN_SCRIPT_GRANTHA = _fitz.UCDN_SCRIPT_GRANTHA

UCDN_SCRIPT_KHOJKI = _fitz.UCDN_SCRIPT_KHOJKI

UCDN_SCRIPT_KHUDAWADI = _fitz.UCDN_SCRIPT_KHUDAWADI

UCDN_SCRIPT_LINEAR_A = _fitz.UCDN_SCRIPT_LINEAR_A

UCDN_SCRIPT_MAHAJANI = _fitz.UCDN_SCRIPT_MAHAJANI

UCDN_SCRIPT_MANICHAEAN = _fitz.UCDN_SCRIPT_MANICHAEAN

UCDN_SCRIPT_MENDE_KIKAKUI = _fitz.UCDN_SCRIPT_MENDE_KIKAKUI

UCDN_SCRIPT_MODI = _fitz.UCDN_SCRIPT_MODI

UCDN_SCRIPT_MRO = _fitz.UCDN_SCRIPT_MRO

UCDN_SCRIPT_NABATAEAN = _fitz.UCDN_SCRIPT_NABATAEAN

UCDN_SCRIPT_OLD_NORTH_ARABIAN = _fitz.UCDN_SCRIPT_OLD_NORTH_ARABIAN

UCDN_SCRIPT_OLD_PERMIC = _fitz.UCDN_SCRIPT_OLD_PERMIC

UCDN_SCRIPT_PAHAWH_HMONG = _fitz.UCDN_SCRIPT_PAHAWH_HMONG

UCDN_SCRIPT_PALMYRENE = _fitz.UCDN_SCRIPT_PALMYRENE

UCDN_SCRIPT_PAU_CIN_HAU = _fitz.UCDN_SCRIPT_PAU_CIN_HAU

UCDN_SCRIPT_PSALTER_PAHLAVI = _fitz.UCDN_SCRIPT_PSALTER_PAHLAVI

UCDN_SCRIPT_SIDDHAM = _fitz.UCDN_SCRIPT_SIDDHAM

UCDN_SCRIPT_TIRHUTA = _fitz.UCDN_SCRIPT_TIRHUTA

UCDN_SCRIPT_WARANG_CITI = _fitz.UCDN_SCRIPT_WARANG_CITI

UCDN_SCRIPT_AHOM = _fitz.UCDN_SCRIPT_AHOM

UCDN_SCRIPT_ANATOLIAN_HIEROGLYPHS = _fitz.UCDN_SCRIPT_ANATOLIAN_HIEROGLYPHS

UCDN_SCRIPT_HATRAN = _fitz.UCDN_SCRIPT_HATRAN

UCDN_SCRIPT_MULTANI = _fitz.UCDN_SCRIPT_MULTANI

UCDN_SCRIPT_OLD_HUNGARIAN = _fitz.UCDN_SCRIPT_OLD_HUNGARIAN

UCDN_SCRIPT_SIGNWRITING = _fitz.UCDN_SCRIPT_SIGNWRITING

UCDN_SCRIPT_ADLAM = _fitz.UCDN_SCRIPT_ADLAM

UCDN_SCRIPT_BHAIKSUKI = _fitz.UCDN_SCRIPT_BHAIKSUKI

UCDN_SCRIPT_MARCHEN = _fitz.UCDN_SCRIPT_MARCHEN

UCDN_SCRIPT_NEWA = _fitz.UCDN_SCRIPT_NEWA

UCDN_SCRIPT_OSAGE = _fitz.UCDN_SCRIPT_OSAGE

UCDN_SCRIPT_TANGUT = _fitz.UCDN_SCRIPT_TANGUT

UCDN_SCRIPT_MASARAM_GONDI = _fitz.UCDN_SCRIPT_MASARAM_GONDI

UCDN_SCRIPT_NUSHU = _fitz.UCDN_SCRIPT_NUSHU

UCDN_SCRIPT_SOYOMBO = _fitz.UCDN_SCRIPT_SOYOMBO

UCDN_SCRIPT_ZANABAZAR_SQUARE = _fitz.UCDN_SCRIPT_ZANABAZAR_SQUARE

UCDN_SCRIPT_DOGRA = _fitz.UCDN_SCRIPT_DOGRA

UCDN_SCRIPT_GUNJALA_GONDI = _fitz.UCDN_SCRIPT_GUNJALA_GONDI

UCDN_SCRIPT_HANIFI_ROHINGYA = _fitz.UCDN_SCRIPT_HANIFI_ROHINGYA

UCDN_SCRIPT_MAKASAR = _fitz.UCDN_SCRIPT_MAKASAR

UCDN_SCRIPT_MEDEFAIDRIN = _fitz.UCDN_SCRIPT_MEDEFAIDRIN

UCDN_SCRIPT_OLD_SOGDIAN = _fitz.UCDN_SCRIPT_OLD_SOGDIAN

UCDN_SCRIPT_SOGDIAN = _fitz.UCDN_SCRIPT_SOGDIAN

UCDN_SCRIPT_ELYMAIC = _fitz.UCDN_SCRIPT_ELYMAIC

UCDN_SCRIPT_NANDINAGARI = _fitz.UCDN_SCRIPT_NANDINAGARI

UCDN_SCRIPT_NYIAKENG_PUACHUE_HMONG = _fitz.UCDN_SCRIPT_NYIAKENG_PUACHUE_HMONG

UCDN_SCRIPT_WANCHO = _fitz.UCDN_SCRIPT_WANCHO

FZ_MIN_INF_RECT = (-2147483648)

FZ_MAX_INF_RECT = (2147483520)

APN = APN[1][2:-2]

APD = APD[1][2:-2]

PDF_OC_ON = (0)

PDF_OC_TOGGLE = (1)

PDF_OC_OFF = (2)

LINK_NONE = (0)

LINK_GOTO = (1)

LINK_URI = (2)

LINK_LAUNCH = (3)

LINK_NAMED = (4)

LINK_GOTOR = (5)

LINK_FLAG_L_VALID = (1)

LINK_FLAG_T_VALID = (2)

LINK_FLAG_R_VALID = (4)

LINK_FLAG_B_VALID = (8)

LINK_FLAG_FIT_H = (16)

LINK_FLAG_FIT_V = (32)

LINK_FLAG_R_IS_ZOOM = (64)

TEXT_ALIGN_LEFT = (0)

TEXT_ALIGN_CENTER = (1)

TEXT_ALIGN_RIGHT = (2)

TEXT_ALIGN_JUSTIFY = (3)

TEXT_OUTPUT_TEXT = (0)

TEXT_OUTPUT_HTML = (1)

TEXT_OUTPUT_JSON = (2)

TEXT_OUTPUT_XML = (3)

TEXT_OUTPUT_XHTML = (4)

TEXT_PRESERVE_LIGATURES = (1)

TEXT_PRESERVE_WHITESPACE = (2)

TEXT_PRESERVE_IMAGES = (4)

TEXT_INHIBIT_SPACES = (8)

TEXT_DEHYPHENATE = (16)

TEXT_PRESERVE_SPANS = (32)

TEXT_MEDIABOX_CLIP = (64)

TEXTFLAGS_WORDS = (TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE | TEXT_MEDIABOX_CLIP)

TEXTFLAGS_BLOCKS = (TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE | TEXT_MEDIABOX_CLIP)

TEXTFLAGS_DICT = (TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE | TEXT_MEDIABOX_CLIP |
    TEXT_PRESERVE_IMAGES)

TEXTFLAGS_RAWDICT = TEXTFLAGS_DICT

TEXTFLAGS_SEARCH = (TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE | TEXT_MEDIABOX_CLIP |
    TEXT_DEHYPHENATE)

TEXTFLAGS_HTML = (TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE | TEXT_MEDIABOX_CLIP |
    TEXT_PRESERVE_IMAGES)

TEXTFLAGS_XHTML = (TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE | TEXT_MEDIABOX_CLIP |
    TEXT_PRESERVE_IMAGES)

TEXTFLAGS_XML = (TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE | TEXT_MEDIABOX_CLIP)

TEXTFLAGS_TEXT = (TEXT_PRESERVE_LIGATURES | TEXT_PRESERVE_WHITESPACE | TEXT_MEDIABOX_CLIP)

TEXT_ENCODING_LATIN = (0)

TEXT_ENCODING_GREEK = (1)

TEXT_ENCODING_CYRILLIC = (2)

CSSFONT = """
@font-face {font-family: %s; src: url(%s);%s%s}
"""

CSS = """"""

W = exp(log(random()) / k)

BT = ap.find(b'BT')

ET = (ap.find(b'ET') + 2)

Q = E.q

LINEHEIGHT = (fontsize * lheight)

UTF = (u' ' + u''.join(map(chr, range(9615, 9607, -1))))

BLANK = """  """

COLOUR_RESET = """[0m"""

COLOUR_RGB = """[38;2;%d;%d;%dm"""

COLOURS = {'BLACK': '\x1b[30m', 'RED': '\x1b[31m', 'GREEN': '\x1b[32m', 'YELLOW':
    '\x1b[33m', 'BLUE': '\x1b[34m', 'MAGENTA': '\x1b[35m', 'CYAN':
    '\x1b[36m', 'WHITE': '\x1b[37m'}

N_BARS = self.default_len

RE_OPTS = re.compile('\\n {4}(\\S+)\\s{2,}:\\s*([^,]+)')

RE_SHLEX = re.compile('\\s*(?<!\\S)--?([^\\s=]+)(\\s+|=|$)')

UNSUPPORTED_OPTS = ('iterable', 'gui', 'out', 'file')

CLI_EXTRA_DOC = """
    Extra CLI Options
    -----------------
    name  : type, optional
        TODO: find out why this is needed.
    delim  : chr, optional
        Delimiting character [default: '\\n']. Use '\\0' for null.
        N.B.: on Windows systems, Python converts '\\n' to '\\r\\n'.
    buf_size  : int, optional
        String buffer size in bytes [default: 256]
        used when `delim` is specified.
    bytes  : bool, optional
        If true, will count bytes, ignore `delim`, and default
        `unit_scale` to True, `unit_divisor` to 1024, and `unit` to 'B'.
    tee  : bool, optional
        If true, passes `stdin` to both `stderr` and `stdout`.
    update  : bool, optional
        If true, will treat input as newly elapsed iterations,
        i.e. numbers to pass to `update()`. Note that this is slow
        (~2e5 it/s) since every input must be decoded as a number.
    update_to  : bool, optional
        If true, will treat input as total elapsed iterations,
        i.e. numbers to assign to `self.n`. Note that this is slow
        (~2e5 it/s) since every input must be decoded as a number.
    null  : bool, optional
        If true, will discard input (no stdout).
    manpath  : str, optional
        Directory in which to install tqdm man pages.
    comppath  : str, optional
        Directory in which to place tqdm completion.
    log  : str, optional
        CRITICAL|FATAL|ERROR|WARN(ING)|[default: 'INFO']|DEBUG|NOTSET.
"""

CUR_OS = sys.platform

IS_WIN = any(CUR_OS.startswith(i) for i in ['win32', 'cygwin'])

IS_NIX = any(CUR_OS.startswith(i) for i in ['aix', 'linux', 'darwin', 'freebsd'])

RE_ANSI = re.compile('\\x1b\\[[;\\d]*[A-Za-z]')

IPY = (0)

WARN_NOIPYW = """IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html"""

API = """https://discord.com/api/v10"""

UA = f"""tqdm (https://tqdm.github.io, {__version__}) {default_user_agent()}"""

ESCAPE_REPLACEMENTS = {'\x00': '0', '\x07': 'a', '\x08': 'b', '\t': 't', '\n': 'n', '\x0b': 'v',
    '\x0c': 'f', '\r': 'r', '\x1b': 'e', '"': '"', '\\': '\\', '\x85': 'N',
    '\xa0': '_', '\u2028': 'L', '\u2029': 'P'}

ESCAPE_CODES = {'x': 2, 'u': 4, 'U': 8}

DEFAULT_TAGS = {'!': '!', '!!': 'tag:yaml.org,2002:'}

NON_PRINTABLE = re.compile('[^\t\n\r -~\x85\xa0-\ud7ff\ue000-�𐀀-\U0010ffff]')

DEFAULT_SCALAR_TAG = """tag:yaml.org,2002:str"""

DEFAULT_SEQUENCE_TAG = """tag:yaml.org,2002:seq"""

DEFAULT_MAPPING_TAG = """tag:yaml.org,2002:map"""

ANCHOR_TEMPLATE = """id%03d"""

DEFAULT_TAG_PREFIXES = {'!': '!', 'tag:yaml.org,2002:': '!!'}

FILE_ATTRIBUTE_HIDDEN = (2)

_VALID_NAME = re.compile('^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$', re.I)

_UNSAFE_NAME_CHARS = re.compile('[^A-Z0-9._-]+', re.I)

_NON_ALPHANUMERIC = re.compile('[^A-Z0-9]+', re.I)

EGG_FRAGMENT = re.compile('^egg=([-A-Za-z0-9_.+!]+)$')

HREF = re.compile('href\\s*=\\s*[\'"]?([^\'"> ]+)', re.I)

PYPI_MD5 = re.compile(
    '<a href="([^"#]+)">([^<]+)</a>\\n\\s+\\(<a (?:title="MD5 hash"\\n\\s+)href="[^?]+\\?:action=show_md5&amp;digest=([0-9a-f]{32})">md5</a>\\)'
    )

URL_SCHEME = re.compile('([-+.a-z0-9]{2,}):', re.I).match

EXTENSIONS = """.tar.gz .tar.bz2 .tar .zip .tgz""".split()

_SOCKET_TIMEOUT = (15)

REL = re.compile('<([^>]*\\srel\\s{0,10}=\\s{0,10}[\'"]?([^\'" >]+)[^>]*)>', re.I)

NO_MATCH_SENTINEL = (None, None)

PY_SOURCE = (1)

PY_COMPILED = (2)

C_EXTENSION = (3)

C_BUILTIN = (6)

PY_FROZEN = (7)

ALWAYS_EXCLUDE = ('ez_setup', '*__pycache__')

_EXCLUDE = ('ci', 'bin', 'debian', 'doc', 'docs', 'documentation', 'manpages', 'news',
    'newsfragments', 'changelog', 'test', 'tests', 'unit_test',
    'unit_tests', 'example', 'examples', 'scripts', 'tools', 'util',
    'utils', 'python', 'build', 'dist', 'venv', 'env', 'requirements',
    'tasks', 'fabfile', 'site_scons', 'benchmark', 'benchmarks', 'exercise',
    'exercises', 'htmlcov', '[._]*')

DEFAULT_EXCLUDE = ('setup', 'conftest', 'test', 'tests', 'example', 'examples', 'build',
    'toxfile', 'noxfile', 'pavement', 'dodo', 'tasks', 'fabfile',
    '[Ss][Cc]onstruct', 'conanfile', 'manage', 'benchmark', 'benchmarks',
    'exercise', 'exercises', '[._]*')

_INDENT = (8 * ' ')

_TEMPLATE = f"""{80 * '*'}
{{details}}
{80 * '*'}"""

STORE_NAME = dis.opmap['STORE_NAME']

STORE_GLOBAL = dis.opmap['STORE_GLOBAL']

LOAD_CONST = dis.opmap['LOAD_CONST']

_SUMMARY = """
        Package {importable!r} is absent from the `packages` configuration.
        """

_DETAILS = """
        ############################
        # Package would be ignored #
        ############################
        Python recognizes {importable!r} as an importable package[^1],
        but it is absent from setuptools' `packages` configuration.

        This leads to an ambiguous overall configuration. If you want to distribute this
        package, please make sure that {importable!r} is explicitly added
        to the `packages` configuration field.

        Alternatively, you can also rely on setuptools' discovery methods
        (for example by using `find_namespace_packages(...)`/`find_namespace:`
        instead of `find_packages(...)`/`find:`).

        You can read more about "package discovery" on setuptools documentation page:

        - https://setuptools.pypa.io/en/latest/userguide/package_discovery.html

        If you don't want {importable!r} to be distributed and are
        already explicitly excluding {importable!r} via
        `find_namespace_packages(...)/find_namespace` or `find_packages(...)/find`,
        you can try to use `exclude_package_data`, or `include-package-data=False` in
        combination with a more fine grained `package-data` configuration.

        You can read more about "package data files" on setuptools documentation page:

        - https://setuptools.pypa.io/en/latest/userguide/datafiles.html


        [^1]: For Python, any directory (with suitable naming) can be imported,
              even if it does not contain any `.py` files.
              On the other hand, currently there is no concept of package data
              directory, all directories are treated like packages.
        """

_MODULES_TO_HIDE = {'setuptools', 'distutils', 'pkg_resources', 'Cython', '_distutils_hack'}

_EXCEPTIONS = []

WRITE_FLAGS = functools.reduce(operator.or_, [getattr(_os, a, 0) for a in
    'O_WRONLY O_RDWR O_APPEND O_CREAT O_TRUNC O_TEMPORARY'.split()])

SETUPTOOLS_ENABLE_FEATURES = os.getenv('SETUPTOOLS_ENABLE_FEATURES', '').lower()

LEGACY_EDITABLE = ('legacy-editable' in SETUPTOOLS_ENABLE_FEATURES.replace('_', '-'))

_DUE_DATE = (2000, 11, 22)

_SEE_URL = """https://github.com/pypa/setuptools/issues/917"""

_BACKEND = _BuildMetaBackend()

HKEY_USERS = None

HKEY_CURRENT_USER = None

HKEY_LOCAL_MACHINE = None

HKEY_CLASSES_ROOT = None

HKEYS = (winreg.HKEY_USERS, winreg.HKEY_CURRENT_USER, winreg.HKEY_LOCAL_MACHINE,
    winreg.HKEY_CLASSES_ROOT)

_DISTUTILS_UNSUPPORTED_METADATA = {'long_description_content_type': lambda : None, 'project_urls': dict,
    'provides_extras': dict, 'license_file': lambda : None, 'license_files':
    lambda : None, 'install_requires': list, 'extras_require': dict}

WHEEL_NAME = re.compile(
    """^(?P<project_name>.+?)-(?P<version>\\d.*?)
    ((-(?P<build>\\d.*?))?-(?P<py_version>.+?)-(?P<abi>.+?)-(?P<platform>.+?)
    )\\.whl$"""
    , re.VERBOSE).match

NAMESPACE_PACKAGE_INIT = """__import__('pkg_resources').declare_namespace(__name__)
"""

LOCALE_ENCODING = ('locale' if sys.version_info >= (3, 10) else None)

PTH_ENCODING = LOCALE_ENCODING

DOLLAR_DIGITS = re.compile('\\$(\\d+)')

FUNCTION_CALL = re.compile('((\\w+)\\([^)]*\\)*)', re.IGNORECASE)

PARTITION_WORD = re.compile('\\A(\\s*)(.+?)(\\s*)\\Z')

PL_SB_POSTFIX_ADJ_STEMS_RE = re.compile(f'^(?:{pl_sb_postfix_adj_stems})$', re.IGNORECASE)

PL_SB_PREP_DUAL_COMPOUND_RE = re.compile(f'^(?:{pl_sb_prep_dual_compound})$', re.IGNORECASE)

DENOMINATOR = re.compile('(?P<denominator>.+)( (per|a) .+)')

PLVERB_SPECIAL_S_RE = re.compile(f'^({plverb_special_s})$')

WHITESPACE = re.compile('\\s')

ENDS_WITH_S = re.compile('^(.*[^s])s$', re.IGNORECASE)

ENDS_WITH_APOSTROPHE_S = re.compile("^(.*)'s?$")

INDEFINITE_ARTICLE_TEST = re.compile('\\A(\\s*)(?:an?\\s+)?(.+?)(\\s*)\\Z', re.IGNORECASE)

SPECIAL_AN = re.compile('^[aefhilmnorsx]$', re.IGNORECASE)

SPECIAL_A = re.compile('^[bcdgjkpqtuvwyz]$', re.IGNORECASE)

SPECIAL_ABBREV_AN = re.compile('^[aefhilmnorsx][.-]', re.IGNORECASE)

SPECIAL_ABBREV_A = re.compile('^[a-z][.-]', re.IGNORECASE)

CONSONANTS = re.compile('^[^aeiouy]', re.IGNORECASE)

ARTICLE_SPECIAL_EU = re.compile('^e[uw]', re.IGNORECASE)

ARTICLE_SPECIAL_ONCE = re.compile('^onc?e\\b', re.IGNORECASE)

ARTICLE_SPECIAL_ONETIME = re.compile('^onetime\\b', re.IGNORECASE)

ARTICLE_SPECIAL_UNIT = re.compile('^uni([^nmd]|mo)', re.IGNORECASE)

ARTICLE_SPECIAL_UBA = re.compile('^u[bcfghjkqrst][aeiou]', re.IGNORECASE)

ARTICLE_SPECIAL_UKR = re.compile('^ukr', re.IGNORECASE)

SPECIAL_CAPITALS = re.compile('^U[NK][AIEO]?')

VOWELS = re.compile('^[aeiou]', re.IGNORECASE)

DIGIT_GROUP = re.compile('(\\d)')

TWO_DIGITS = re.compile('(\\d)(\\d)')

THREE_DIGITS = re.compile('(\\d)(\\d)(\\d)')

THREE_DIGITS_WORD = re.compile('(\\d)(\\d)(\\d)(?=\\D*\\Z)')

TWO_DIGITS_WORD = re.compile('(\\d)(\\d)(?=\\D*\\Z)')

ONE_DIGIT_WORD = re.compile('(\\d)(?=\\D*\\Z)')

FOUR_DIGIT_COMMA = re.compile('(\\d)(\\d{3}(?:,|\\Z))')

NON_DIGIT = re.compile('\\D')

WHITESPACES_COMMA = re.compile('\\s+,')

COMMA_WORD = re.compile(', (\\S+)\\s+\\Z')

WHITESPACES = re.compile('\\s+')

PRESENT_PARTICIPLE_REPLACEMENTS = ((re.compile('ie$'), 'y'), (re.compile('ue$'), 'u'), (re.compile(
    '([auy])e$'), '\\g<1>'), (re.compile('ski$'), 'ski'), (re.compile(
    '[^b]i$'), ''), (re.compile('^(are|were)$'), 'be'), (re.compile(
    '^(had)$'), 'hav'), (re.compile('^(hoe)$'), '\\g<1>'), (re.compile(
    '([^e])e$'), '\\g<1>'), (re.compile('er$'), 'er'), (re.compile(
    '([^aeiou][aeiouy]([bdgmnprst]))$'), '\\g<1>\\g<2>'))

DIGIT = re.compile('\\d')

_STATIC_TYPE_CHECKING = TYPE_CHECKING

_VT = TypeVar('_VT')

FAT_MAGIC = (3405691582)

FAT_CIGAM = (3199925962)

FAT_MAGIC_64 = (3405691583)

FAT_CIGAM_64 = (3216703178)

MH_MAGIC = (4277009102)

MH_CIGAM = (3472551422)

MH_MAGIC_64 = (4277009103)

MH_CIGAM_64 = (3489328638)

LC_VERSION_MIN_MACOSX = (36)

LC_BUILD_VERSION = (50)

CPU_TYPE_ARM64 = (16777228)

PY_LIMITED_API_PATTERN = """cp3\\d"""

WHEEL_INFO_RE = re.compile(
    """^(?P<namever>(?P<name>[^\\s-]+?)-(?P<ver>[^\\s-]+?))(-(?P<build>\\d[^\\s-]*))?
     -(?P<pyver>[^\\s-]+?)-(?P<abi>[^\\s-]+?)-(?P<plat>\\S+)\\.whl$"""
    , re.VERBOSE)

MINIMUM_TIMESTAMP = (315532800)

DIST_INFO_RE = re.compile('^(?P<namever>(?P<name>.+?)-(?P<ver>\\d.*?))\\.dist-info$')

TAGS_HELP = """Make a new wheel with given tags. Any tags unspecified will remain the same.
Starting the tags with a "+" will append to the existing tags. Starting with a
"-" will remove a tag (use --option=-TAG syntax). Multiple tags can be
separated by ".". The original file will remain unless --remove is given.  The
output filename(s) will be displayed on stdout for further processing.
"""

_EMPTY_HASH = hash(range(0, 0))

NUL = b'\x00'

BLOCKSIZE = (512)

RECORDSIZE = (BLOCKSIZE * 20)

GNU_MAGIC = b'ustar  \x00'

POSIX_MAGIC = b'ustar\x0000'

LENGTH_NAME = (100)

LENGTH_LINK = (100)

LENGTH_PREFIX = (155)

REGTYPE = b'0'

AREGTYPE = b'\x00'

LNKTYPE = b'1'

SYMTYPE = b'2'

CHRTYPE = b'3'

BLKTYPE = b'4'

DIRTYPE = b'5'

FIFOTYPE = b'6'

CONTTYPE = b'7'

GNUTYPE_LONGNAME = b'L'

GNUTYPE_LONGLINK = b'K'

GNUTYPE_SPARSE = b'S'

XHDTYPE = b'x'

XGLTYPE = b'g'

SOLARIS_XHDTYPE = b'X'

USTAR_FORMAT = (0)

GNU_FORMAT = (1)

PAX_FORMAT = (2)

DEFAULT_FORMAT = PAX_FORMAT

SUPPORTED_TYPES = (REGTYPE, AREGTYPE, LNKTYPE, SYMTYPE, DIRTYPE, FIFOTYPE, CONTTYPE, CHRTYPE,
    BLKTYPE, GNUTYPE_LONGNAME, GNUTYPE_LONGLINK, GNUTYPE_SPARSE)

REGULAR_TYPES = (REGTYPE, AREGTYPE, CONTTYPE, GNUTYPE_SPARSE)

GNU_TYPES = (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK, GNUTYPE_SPARSE)

PAX_FIELDS = ('path', 'linkpath', 'size', 'mtime', 'uid', 'gid', 'uname', 'gname')

PAX_NAME_FIELDS = {'path', 'linkpath', 'uname', 'gname'}

PAX_NUMBER_FIELDS = {'atime': float, 'ctime': float, 'mtime': float, 'uid': int, 'gid': int,
    'size': int}

ENCODING = """utf-8"""

_NAMED_FILTERS = {'fully_trusted': fully_trusted_filter, 'tar': tar_filter, 'data': data_filter}

_KEEP = object()

OPEN_METH = {'tar': 'taropen', 'gz': 'gzopen', 'bz2': 'bz2open', 'xz': 'xzopen'}

_DOCSTRING_SPLIT = compile_regex('\\n\\s*-{4,}\\s*\\n')

BINARY_MAGIC_METHODS = {'__add__', '__and__', '__cmp__', '__divmod__', '__div__', '__eq__',
    '__floordiv__', '__ge__', '__gt__', '__iadd__', '__iand__', '__idiv__',
    '__ifloordiv__', '__ilshift__', '__imatmul__', '__imod__', '__imul__',
    '__ior__', '__ipow__', '__irshift__', '__isub__', '__itruediv__',
    '__ixor__', '__le__', '__lshift__', '__lt__', '__matmul__', '__mod__',
    '__mul__', '__ne__', '__or__', '__pow__', '__radd__', '__rand__',
    '__rdiv__', '__rfloordiv__', '__rlshift__', '__rmatmul__', '__rmod__',
    '__rmul__', '__ror__', '__rpow__', '__rrshift__', '__rshift__',
    '__rsub__', '__rtruediv__', '__rxor__', '__sub__', '__truediv__', '__xor__'
    }

OPTIMIZATION = """typeguard"""

WARN = (1)

IGNORE = auto()

FIRST_ITEM = auto()

ALL_ITEMS = auto()

_SEE_DOCS = """userguide/development_mode.html"""

_CONTENT_TYPES = {'.md': 'text/markdown', '.rst': 'text/x-rst', '.txt': 'text/plain'}

TOOL_TABLE_RENAMES = {'script_files': 'scripts'}

TOOL_TABLE_REMOVALS = {'namespace_packages':
    """
        Please migrate to implicit native namespaces instead.
        See https://packaging.python.org/en/latest/guides/packaging-namespace-packages/.
        """
    }

SETUPTOOLS_PATCHES = {'long_description_content_type', 'project_urls', 'provides_extras',
    'license_file', 'license_files'}

_PREPROCESS = {'ext_modules': _ext_modules}

_PREVIOUSLY_DEFINED = {'name': _attrgetter('metadata.name'), 'version': _attrgetter(
    'metadata.version'), 'description': _attrgetter('metadata.description'),
    'readme': _attrgetter('metadata.long_description'), 'requires-python':
    _some_attrgetter('python_requires', 'metadata.python_requires'),
    'license': _attrgetter('metadata.license'), 'authors': _some_attrgetter
    ('metadata.author', 'metadata.author_email'), 'maintainers':
    _some_attrgetter('metadata.maintainer', 'metadata.maintainer_email'),
    'keywords': _attrgetter('metadata.keywords'), 'classifiers':
    _attrgetter('metadata.classifiers'), 'urls': _attrgetter(
    'metadata.project_urls'), 'entry-points': _get_previous_entrypoints,
    'scripts': _get_previous_scripts, 'gui-scripts':
    _get_previous_gui_scripts, 'dependencies': _attrgetter(
    'install_requires'), 'optional-dependencies': _attrgetter('extras_require')
    }

_K = TypeVar('_K')

SPLIT_RE = re.compile('[\\.\\[\\]]+')

_DESC = """According to PEP 621:

    Build back-ends MUST raise an error if the metadata specifies a field
    statically as well as being listed in dynamic.
    """

_URL = """https://packaging.python.org/en/latest/specifications/pyproject-toml/#dynamic"""

EXTRA_VALIDATIONS = (validate_project_dynamic,)

_MESSAGE_REPLACEMENTS = {'must be named by propertyName definition': 'keys must be named by',
    'one of contains definition': 'at least one item that matches',
    ' same as const definition:': '', 'only specified items':
    'only items matching the definition'}

_SKIP_DETAILS = ('must not be empty', 'is always invalid', 'must not be there')

_NEED_DETAILS = {'anyOf', 'oneOf', 'allOf', 'contains', 'propertyNames', 'not', 'items'}

_CAMEL_CASE_SPLITTER = re.compile('\\W+|([A-Z][^A-Z\\W]*)')

_IDENTIFIER = re.compile('^[\\w_]+$', re.I)

_TOML_JARGON = {'object': 'table', 'property': 'key', 'properties': 'keys',
    'property names': 'keys'}

_FORMATS_HELP = """
For more details about `format` see
https://validate-pyproject.readthedocs.io/en/latest/api/validate_pyproject.formats.html
"""

_IGNORE = frozenset(('description', 'default', 'title', 'examples'))

REGEX_PATTERNS = {'^.*$': re.compile('^.*$'), '.+': re.compile('.+'), '^.+$': re.compile(
    '^.+$'), 'idn-email_re_pattern': re.compile('^[^@]+@[^@]+\\.[^@]+\\Z')}

VERSION_REGEX = re.compile('^\\s*' + VERSION_PATTERN + '\\s*$', re.X | re.I)

PEP508_IDENTIFIER_PATTERN = """([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])"""

PEP508_IDENTIFIER_REGEX = re.compile(f'^{PEP508_IDENTIFIER_PATTERN}$', re.I)

ENTRYPOINT_PATTERN = """[^\\[\\s=]([^=]*[^\\s=])?"""

ENTRYPOINT_REGEX = re.compile(f'^{ENTRYPOINT_PATTERN}$', re.I)

RECOMMEDED_ENTRYPOINT_PATTERN = """[\\w.-]+"""

RECOMMEDED_ENTRYPOINT_REGEX = re.compile(f'^{RECOMMEDED_ENTRYPOINT_PATTERN}$', re.I)

ENTRYPOINT_GROUP_PATTERN = """\\w+(\\.\\w+)*"""

ENTRYPOINT_GROUP_REGEX = re.compile(f'^{ENTRYPOINT_GROUP_PATTERN}$', re.I)

EXAMPLE_WITH_MANIFEST = {'setup.cfg': DALS(
    """
        [metadata]
        name = mypkg
        version = 42

        [options]
        include_package_data = True
        packages = find:

        [options.packages.find]
        exclude = *.tests*
        """
    ), 'mypkg': {'__init__.py': '', 'resource_file.txt': '', 'tests': {
    '__init__.py': '', 'test_mypkg.py': '', 'test_file.txt': ''}},
    'MANIFEST.in': DALS(
    """
        global-include *.py *.txt
        global-exclude *.py[cod]
        prune dist
        prune build
        prune *.egg-info
        """
    )}

EXAMPLE_ARBITRARY_MAPPING = {'pyproject.toml': DALS(
    """
        [project]
        name = "mypkg"
        version = "42"

        [tool.setuptools]
        packages = ["mypkg", "mypkg.sub1", "mypkg.sub2", "mypkg.sub2.nested"]

        [tool.setuptools.package-dir]
        "" = "src"
        "mypkg.sub2" = "src/mypkg/_sub2"
        "mypkg.sub2.nested" = "other"
        """
    ), 'src': {'mypkg': {'__init__.py': '', 'resource_file.txt': '', 'sub1':
    {'__init__.py': '', 'mod1.py': ''}, '_sub2': {'mod2.py': ''}}}, 'other':
    {'__init__.py': '', 'mod3.py': ''}, 'MANIFEST.in': DALS(
    """
        global-include *.py *.txt
        global-exclude *.py[cod]
        """
    )}

PYPROJECTS = {'default_pyproject': DALS(
    """
            [project]
            name = "foo"
            version = "1"
            """
    ), 'dont_include_package_data': DALS(
    """
            [project]
            name = "foo"
            version = "1"

            [tool.setuptools]
            include-package-data = false
            """
    ), 'exclude_type_info': DALS(
    """
            [project]
            name = "foo"
            version = "1"

            [tool.setuptools]
            include-package-data = false

            [tool.setuptools.exclude-package-data]
            "*" = ["py.typed", "*.pyi"]
            """
    )}

EXAMPLES = [('pip', LATEST), ('pytest', LATEST), ('mypy', LATEST), ('botocore', LATEST
    ), ('kiwisolver', LATEST), ('brotli', LATEST), ('pyyaml', LATEST), (
    'charset-normalizer', LATEST), ('protobuf', LATEST), ('requests',
    LATEST), ('celery', LATEST)]

SETUP_SCRIPT_STUB = """__import__('setuptools').setup()"""

TIMEOUT = int(os.getenv('TIMEOUT_BACKEND_TEST', '180'))

_EXAMPLES = {'default': dict(args=('Hello {x}', """
	{target} {v:.1f}"""), kwargs={'x':
    5, 'v': 3, 'target': 'World'}, expected=
    """
    Hello 5
    !!

            ********************************************************************************
            World 3.0
            ********************************************************************************

    !!
    """
    ), 'futue_due_date': dict(args=('Summary', 'Lorem ipsum'), kwargs={
    'due_date': (9999, 11, 22)}, expected=
    """
    Summary
    !!

            ********************************************************************************
            Lorem ipsum

            By 9999-Nov-22, you need to update your project and remove deprecated calls
            or your builds will no longer be supported.
            ********************************************************************************

    !!
    """
    ), 'past_due_date_with_docs': dict(args=('Summary', 'Lorem ipsum'),
    kwargs={'due_date': (2000, 11, 22), 'see_docs': 'some_page.html'},
    expected=
    """
    Summary
    !!

            ********************************************************************************
            Lorem ipsum

            This deprecation is overdue, please update your project and remove deprecated
            calls to avoid build errors in the future.

            See https://setuptools.pypa.io/en/latest/some_page.html for details.
            ********************************************************************************

    !!
    """
    )}

_TEXT_KWARGS = {'text': True, 'encoding': 'utf-8'}

ENSURE_IMPORTS_ARE_NOT_DUPLICATED = """
# Depending on the importlib machinery and _distutils_hack, some imports are
# duplicated resulting in different module objects being loaded, which prevents
# patches as shown in #3042.
# This script provides a way of verifying if this duplication is happening.

from distutils import cmd
import distutils.command.sdist as sdist

# import last to prevent caching
from distutils import {imported_module}

for mod in (cmd, sdist):
    assert mod.{imported_module} == {imported_module}, (
        f"\\n{{mod.dir_util}}\\n!=\\n{{{imported_module}}}"
    )

print("success")
"""

ENSURE_LOG_IMPORT_IS_NOT_DUPLICATED = """
import types
import distutils.dist as dist
from distutils import log
if isinstance(dist.log, types.ModuleType):
    assert dist.log == log, f"\\n{dist.log}\\n!=\\n{log}"
print("success")
"""

ENSURE_CONSISTENT_ERROR_FROM_MODIFIED_PY = """
from setuptools.modified import newer
from {imported_module}.errors import DistutilsError

# Can't use pytest.raises in this context
try:
    newer("", "")
except DistutilsError:
    print("success")
else:
    raise AssertionError("Expected to raise")
"""

EXAMPLE_BASE_INFO = dict(name='package', version='0.0.1', author='Foo Bar', author_email=
    'foo@bar.net', long_description='Long\ndescription', description=
    'Short description', keywords=['one', 'two'])

HERE = os.path.abspath(os.path.dirname(__file__))

EXAMPLES_FILE = """setupcfg_examples.txt"""

SETUP_ATTRS = {'name': 'sdist_test', 'version': '0.0', 'packages': ['sdist_test'],
    'package_data': {'sdist_test': ['*.txt']}, 'data_files': [('data', [os.
    path.join('d', 'e.dat')])]}

SETUP_PY = """
from distutils.core import setup
import somecode

setup(name='fake')
"""

MANIFEST_IN = """include ok
include xo
exclude xo
include foo.tmp
include buildout.cfg
global-include *.x
global-include *.txt
global-exclude *.tmp
recursive-include f *.oo
recursive-exclude global *.x
graft dir
prune dir3
"""

WHEEL_INFO_TESTS = (('invalid.whl', ValueError), ('simplewheel-2.0-1-py2.py3-none-any.whl', {
    'project_name': 'simplewheel', 'version': '2.0', 'build': '1',
    'py_version': 'py2.py3', 'abi': 'none', 'platform': 'any'}), (
    'simple.dist-0.1-py2.py3-none-any.whl', {'project_name': 'simple.dist',
    'version': '0.1', 'build': None, 'py_version': 'py2.py3', 'abi': 'none',
    'platform': 'any'}), ('example_pkg_a-1-py3-none-any.whl', {
    'project_name': 'example_pkg_a', 'version': '1', 'build': None,
    'py_version': 'py3', 'abi': 'none', 'platform': 'any'}), (
    'PyQt5-5.9-5.9.1-cp35.cp36.cp37-abi3-manylinux1_x86_64.whl', {
    'project_name': 'PyQt5', 'version': '5.9', 'build': '5.9.1',
    'py_version': 'cp35.cp36.cp37', 'abi': 'abi3', 'platform':
    'manylinux1_x86_64'}))

OPTIONS = {'explicit-src': {'package_dir': {'': 'src'}, 'packages': ['pkg']},
    'variation-lib': {'package_dir': {'': 'lib'}}, 'explicit-flat': {
    'packages': ['pkg']}, 'explicit-single_module': {'py_modules': ['pkg']},
    'explicit-namespace': {'packages': ['ns', 'ns.pkg']}, 'automatic-src':
    {}, 'automatic-flat': {}, 'automatic-single_module': {},
    'automatic-namespace': {}}

PURPOSEFULLY_EMPY = {'setup.cfg': DALS(
    """
            [metadata]
            name = myproj
            version = 0.0.0

            [options]
            {param} =
            """
    ), 'setup.py': DALS(
    """
            __import__('setuptools').setup(
                name="myproj",
                version="0.0.0",
                {param}=[]
            )
            """
    ), 'pyproject.toml': DALS(
    """
            [build-system]
            requires = []
            build-backend = 'setuptools.build_meta'

            [project]
            name = "myproj"
            version = "0.0.0"

            [tool.setuptools]
            {param} = []
            """
    ), 'template-pyproject.toml': DALS(
    """
            [build-system]
            requires = []
            build-backend = 'setuptools.build_meta'
            """
    )}

DEFAULT_VERSION = """0.0.0"""

EXAMPLE_SETUPCFG = """
    [metadata]
    name = proj
    version = 42

    [options]
    include_package_data = True
    """

EXAMPLE_PYPROJECT = """
    [project]
    name = "proj"
    version = "42"
    """

PYPROJECT_PACKAGE_DIR = """
    [tool.setuptools]
    package-dir = {"" = "src"}
    """

CHECK_PACKAGE_DATA_TESTS = (({'': ['*.txt', '*.rst'], 'hello': ['*.msg']}, None), ((('', ['*.txt',
    '*.rst']), ('hello', ['*.msg'])),
    "'package_data' must be a dictionary mapping package names to lists of string wildcard patterns"
    ), ({(400): ['*.txt', '*.rst']},
    "keys of 'package_data' dict must be strings (got 400)"), ({'hello':
    '*.msg'},
    '"values of \'package_data\' dict" must be of type <tuple[str, ...] | list[str]> (got \'*.msg\')'
    ), ({'hello': (x for x in 'generator')},
    '"values of \'package_data\' dict" must be of type <tuple[str, ...] | list[str]> (got <generator object'
    ))

DEFAULT_FILES = {'dummy_dist-1.0.dist-info/top_level.txt',
    'dummy_dist-1.0.dist-info/METADATA', 'dummy_dist-1.0.dist-info/WHEEL',
    'dummy_dist-1.0.dist-info/RECORD'}

DEFAULT_LICENSE_FILES = {'LICENSE', 'LICENSE.txt', 'LICENCE', 'LICENCE.txt', 'COPYING',
    'COPYING.md', 'NOTICE', 'NOTICE.rst', 'AUTHORS', 'AUTHORS.txt'}

OTHER_IGNORED_FILES = {'LICENSE~', 'AUTHORS~'}

SETUPPY_EXAMPLE = """from setuptools import setup

setup(
    name='dummy_dist',
    version='1.0',
)
"""

UTF8_PKG_INFO = """Metadata-Version: 2.1
Name: helloworld
Version: 42
Author-email: "John X. Ãørçeč" <john@utf8.org>, Γαμα קּ 東 <gama@utf8.org>


UTF-8 描述 説明
"""

EXTENSION_EXAMPLE = """#include <Python.h>

static PyMethodDef methods[] = {
  { NULL, NULL, 0, NULL }
};

static struct PyModuleDef module_def = {
  PyModuleDef_HEAD_INIT,
  "extension",
  "Dummy extension module",
  -1,
  methods
};

PyMODINIT_FUNC PyInit_extension(void) {
  return PyModule_Create(&module_def);
}
"""

EXTENSION_SETUPPY = """from __future__ import annotations

from setuptools import Extension, setup

setup(
    name="extension.dist",
    version="0.1",
    description="A testing distribution ☃",
    ext_modules=[Extension(name="extension", sources=["extension.c"])],
)
"""

INIT_PY = """print "foo\"
"""

EXAMPLE = """
[project]
name = "myproj"
keywords = ["some", "key", "words"]
dynamic = ["version", "readme"]
requires-python = ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*"
dependencies = [
    'importlib-metadata>=0.12;python_version<"3.8"',
    'importlib-resources>=1.0;python_version<"3.7"',
    'pathlib2>=2.3.3,<3;python_version < "3.4" and sys.platform != "win32"',
]

[project.optional-dependencies]
docs = [
    "sphinx>=3",
    "sphinx-argparse>=0.2.5",
    "sphinx-rtd-theme>=0.4.3",
]
testing = [
    "pytest>=1",
    "coverage>=3,<5",
]

[project.scripts]
exec = "pkg.__main__:exec"

[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
package-dir = {"" = "src"}
zip-safe = true
platforms = ["any"]

[tool.setuptools.packages.find]
where = ["src"]

[tool.setuptools.cmdclass]
sdist = "pkg.mod.CustomSdist"

[tool.setuptools.dynamic.version]
attr = "pkg.__version__.VERSION"

[tool.setuptools.dynamic.readme]
file = ["README.md"]
content-type = "text/markdown"

[tool.setuptools.package-data]
"*" = ["*.txt"]

[tool.setuptools.data-files]
"data" = ["_files/*.txt"]

[tool.distutils.sdist]
formats = "gztar"

[tool.distutils.bdist_wheel]
universal = true
"""

PYPROJECT = """        [build-system]
        requires = ["setuptools"]
        build-backend = "setuptools.build_meta"

        [project]
        name = "mypkg"
        version = "3.14159"
        """

EXTENSION = Extension(name='sdist_test.f', sources=[os.path.join('sdist_test', 'f.c')],
    depends=[os.path.join('sdist_test', 'f.h')])

EXTENSION_SOURCES = (EXTENSION.sources + EXTENSION.depends)

_INVALID_PATHS = {'must be relative': lambda : os.path.abspath(os.path.join('sdist_test',
    'f.h')), "can't have `..` segments": lambda : os.path.join('sdist_test',
    '..', 'sdist_test', 'f.h'), "doesn't exist": lambda : os.path.join(
    'sdist_test', 'this_file_does_not_exist.h'),
    'must be inside the project root': lambda : symlink_or_skip_test(touch(
    os.path.join('..', 'outside_of_project_root.h')), 'symlink.h')}

_EXAMPLE_DIRECTIVES = {'setup.cfg - long_description and version':
    """
            [metadata]
            name = testing
            version = file: src/VERSION.txt
            license_files = DOWHATYOUWANT
            long_description = file: README.rst, USAGE.rst
            """
    , 'pyproject.toml - static readme/license files and dynamic version':
    """
            [project]
            name = "testing"
            readme = "USAGE.rst"
            license = {file = "DOWHATYOUWANT"}
            dynamic = ["version"]
            [tool.setuptools.dynamic]
            version = {file = ["src/VERSION.txt"]}
            """
    , 'pyproject.toml - directive with str instead of list':
    """
            [project]
            name = "testing"
            readme = "USAGE.rst"
            license = {file = "DOWHATYOUWANT"}
            dynamic = ["version"]
            [tool.setuptools.dynamic]
            version = {file = "src/VERSION.txt"}
            """
    }

SETUPCFG = DALS(
    """
    [metadata]
    name = {name}
    version = {version}

    [options]
    install_requires =
        foo>=12; sys_platform != "linux"

    [options.extras_require]
    test = pytest

    [options.entry_points]
    console_scripts =
        executable-name = my_package.module:function
    discover =
        myproj = my_package.other_module:function
    """
    )

EGG_INFO_OPTS = [('', ''), ('.post', """[egg_info]
tag_build = post
"""), ('.post',
    """[egg_info]
tag_build = .post
"""), ('.post',
    """[egg_info]
tag_build = post
tag_date = 1
"""), ('.dev',
    """[egg_info]
tag_build = .dev
"""), ('.dev',
    """[egg_info]
tag_build = .dev
tag_date = 1
"""), ('a1',
    """[egg_info]
tag_build = .a1
"""), ('+local',
    """[egg_info]
tag_build = +local
""")]

ENTRY_POINTS = {'console_scripts': {'a': 'mod.a:func'}, 'gui_scripts': {'b': 'mod.b:func'},
    'other': {'c': 'mod.c:func [extra]'}}

PEP621_EXAMPLE = """[project]
name = "spam"
version = "2020.0.0"
description = "Lovely Spam! Wonderful Spam!"
readme = "README.rst"
requires-python = ">=3.8"
license = {file = "LICENSE.txt"}
keywords = ["egg", "bacon", "sausage", "tomatoes", "Lobster Thermidor"]
authors = [
  {email = "hi@pradyunsg.me"},
  {name = "Tzu-Ping Chung"}
]
maintainers = [
  {name = "Brett Cannon", email = "brett@python.org"},
  {name = "John X. Ãørçeč", email = "john@utf8.org"},
  {name = "Γαμα קּ 東", email = "gama@utf8.org"},
]
classifiers = [
  "Development Status :: 4 - Beta",
  "Programming Language :: Python"
]

dependencies = [
  "httpx",
  "gidgethub[httpx]>4.0.0",
  "django>2.1; os_name != 'nt'",
  "django>2.0; os_name == 'nt'"
]

[project.optional-dependencies]
test = [
  "pytest < 5.0.0",
  "pytest-cov[all]"
]

[project.urls]
homepage = "http://example.com"
documentation = "http://readthedocs.org"
repository = "http://github.com"
changelog = "http://github.com/me/spam/blob/master/CHANGELOG.md"

[project.scripts]
spam-cli = "spam:main_cli"

[project.gui-scripts]
spam-gui = "spam:main_gui"

[project.entry-points."spam.magical"]
tomatoes = "spam:main_tomatoes\"
"""

PEP621_INTERNATIONAL_EMAIL_EXAMPLE = """[project]
name = "spam"
version = "2020.0.0"
authors = [
  {email = "hi@pradyunsg.me"},
  {name = "Tzu-Ping Chung"}
]
maintainers = [
  {name = "Степан Бандера", email = "криївка@оун-упа.укр"},
]
"""

PEP621_EXAMPLE_SCRIPT = """
def main_cli(): pass
def main_gui(): pass
def main_tomatoes(): pass
"""

NAME_REMOVE = ('http://', 'https://', 'github.com/', '/raw/')

DOWNLOAD_DIR = Path(__file__).parent

EXTRA_BUILD_DEPS = {'pyyaml': ('Cython<3.0',), 'charset-normalizer': ('mypy>=1.4.1',)}

EXTRA_ENV_VARS = {'pyyaml': {'PYYAML_FORCE_CYTHON': '1'}, 'charset-normalizer': {
    'CHARSET_NORMALIZER_USE_MYPYC': '1'}}

IMPORT_NAME = {'pyyaml': 'yaml', 'protobuf': 'google.protobuf'}

VIRTUALENV = (sys.executable, '-m', 'virtualenv')

INSTALL_OPTIONS = ('--ignore-installed', '--no-build-isolation')

_ORIGINAL_SUBCOMMANDS = {'build_py', 'build_clib', 'build_ext', 'build_scripts'}

INSTALL_DIRECTORY_ATTRS = ['install_lib', 'install_dir', 'install_data', 'install_base']

INSTALL_SCHEMES = {'posix_prefix': {'purelib':
    '{base}/lib/{implementation_lower}{py_version_short}/site-packages',
    'platlib':
    '{platbase}/{platlibdir}/{implementation_lower}{py_version_short}/site-packages'
    , 'headers':
    '{base}/include/{implementation_lower}{py_version_short}{abiflags}/{dist_name}'
    , 'scripts': '{base}/bin', 'data': '{base}'}, 'posix_home': {'purelib':
    '{base}/lib/{implementation_lower}', 'platlib':
    '{base}/{platlibdir}/{implementation_lower}', 'headers':
    '{base}/include/{implementation_lower}/{dist_name}', 'scripts':
    '{base}/bin', 'data': '{base}'}, 'nt': WINDOWS_SCHEME, 'pypy': {
    'purelib': '{base}/site-packages', 'platlib': '{base}/site-packages',
    'headers': '{base}/include/{dist_name}', 'scripts': '{base}/bin',
    'data': '{base}'}, 'pypy_nt': {'purelib': '{base}/site-packages',
    'platlib': '{base}/site-packages', 'headers':
    '{base}/include/{dist_name}', 'scripts': '{base}/Scripts', 'data':
    '{base}'}}

DEFAULT_SCHEME = dict(install_dir='$base/Lib/site-packages', script_dir='$base/Scripts')

_QUOTES = """"'"""

_P = TypeVar('_P', bound=StrPath)

STRICT = """strict"""

LENIENT = """lenient"""

_STRICT_WARNING = """
New or renamed files may not be automatically picked up without a new installation.
"""

_LENIENT_WARNING = """
Options like `package-data`, `include/exclude-package-data` or
`packages.find.exclude/include` may have no effect.
"""

_FINDER_TEMPLATE = """from __future__ import annotations
import sys
from importlib.machinery import ModuleSpec, PathFinder
from importlib.machinery import all_suffixes as module_suffixes
from importlib.util import spec_from_file_location
from itertools import chain
from pathlib import Path

MAPPING: dict[str, str] = {mapping!r}
NAMESPACES: dict[str, list[str]] = {namespaces!r}
PATH_PLACEHOLDER = {name!r} + ".__path_hook__"


class _EditableFinder:  # MetaPathFinder
    @classmethod
    def find_spec(cls, fullname: str, path=None, target=None) -> ModuleSpec | None:  # type: ignore
        # Top-level packages and modules (we know these exist in the FS)
        if fullname in MAPPING:
            pkg_path = MAPPING[fullname]
            return cls._find_spec(fullname, Path(pkg_path))

        # Handle immediate children modules (required for namespaces to work)
        # To avoid problems with case sensitivity in the file system we delegate
        # to the importlib.machinery implementation.
        parent, _, child = fullname.rpartition(".")
        if parent and parent in MAPPING:
            return PathFinder.find_spec(fullname, path=[MAPPING[parent]])

        # Other levels of nesting should be handled automatically by importlib
        # using the parent path.
        return None

    @classmethod
    def _find_spec(cls, fullname: str, candidate_path: Path) -> ModuleSpec | None:
        init = candidate_path / "__init__.py"
        candidates = (candidate_path.with_suffix(x) for x in module_suffixes())
        for candidate in chain([init], candidates):
            if candidate.exists():
                return spec_from_file_location(fullname, candidate)
        return None


class _EditableNamespaceFinder:  # PathEntryFinder
    @classmethod
    def _path_hook(cls, path) -> type[_EditableNamespaceFinder]:
        if path == PATH_PLACEHOLDER:
            return cls
        raise ImportError

    @classmethod
    def _paths(cls, fullname: str) -> list[str]:
        paths = NAMESPACES[fullname]
        if not paths and fullname in MAPPING:
            paths = [MAPPING[fullname]]
        # Always add placeholder, for 2 reasons:
        # 1. __path__ cannot be empty for the spec to be considered namespace.
        # 2. In the case of nested namespaces, we need to force
        #    import machinery to query _EditableNamespaceFinder again.
        return [*paths, PATH_PLACEHOLDER]

    @classmethod
    def find_spec(cls, fullname: str, target=None) -> ModuleSpec | None:  # type: ignore
        if fullname in NAMESPACES:
            spec = ModuleSpec(fullname, None, is_package=True)
            spec.submodule_search_locations = cls._paths(fullname)
            return spec
        return None

    @classmethod
    def find_module(cls, _fullname) -> None:
        return None


def install():
    if not any(finder == _EditableFinder for finder in sys.meta_path):
        sys.meta_path.append(_EditableFinder)

    if not NAMESPACES:
        return

    if not any(hook == _EditableNamespaceFinder._path_hook for hook in sys.path_hooks):
        # PathEntryFinder is needed to create NamespaceSpec without private APIS
        sys.path_hooks.append(_EditableNamespaceFinder._path_hook)
    if PATH_PLACEHOLDER not in sys.path:
        sys.path.append(PATH_PLACEHOLDER)  # Used just to trigger the path hook
"""

_IMPLICIT_DATA_FILES = ('*.pyi', 'py.typed')

README_EXTENSIONS = ['', '.rst', '.txt', '.md']

READMES = ('README', 'README.txt', 'README.rst')

PLAT_SPEC_TO_RUNTIME = {'x86': 'x86', 'x86_amd64': 'x64', 'x86_arm': 'arm', 'x86_arm64': 'arm64'}

SHARED_OBJECT = """shared_object"""

SHARED_LIBRARY = """shared_library"""

EXECUTABLE = """executable"""

ARCHIVE_FORMATS = {'gztar': (make_tarball, [('compress', 'gzip')], "gzip'ed tar-file"),
    'bztar': (make_tarball, [('compress', 'bzip2')], "bzip2'ed tar-file"),
    'xztar': (make_tarball, [('compress', 'xz')], "xz'ed tar-file"), 'ztar':
    (make_tarball, [('compress', 'compress')], 'compressed tar file'),
    'tar': (make_tarball, [('compress', None)], 'uncompressed tar file'),
    'zip': (make_zipfile, [], 'ZIP file')}

INFO = logging.INFO

FATAL = logging.FATAL

TARGET_TO_PLAT = {'x86': 'win32', 'x64': 'win-amd64', 'arm': 'win-arm32', 'arm64': 'win-arm64'}

MACOSX_VERSION_VAR = """MACOSX_DEPLOYMENT_TARGET"""

WS_TRANS = {ord(_wschar): ' ' for _wschar in string.whitespace}

USAGE = """usage: %(script)s [global_opts] cmd1 [cmd1_opts] [cmd2 [cmd2_opts] ...]
   or: %(script)s --help [cmd1 cmd2 ...]
   or: %(script)s --help-commands
   or: %(script)s cmd --help
"""

CONFIG_H_OK = """ok"""

CONFIG_H_NOTOK = """not ok"""

CONFIG_H_UNCERTAIN = """uncertain"""

PREFIX = os.path.normpath(sys.prefix)

EXEC_PREFIX = os.path.normpath(sys.exec_prefix)

BASE_PREFIX = os.path.normpath(sys.base_prefix)

BASE_EXEC_PREFIX = os.path.normpath(sys.base_exec_prefix)

_METHOD_BASENAMES = ('name', 'version', 'author', 'author_email', 'maintainer',
    'maintainer_email', 'url', 'license', 'description', 'long_description',
    'keywords', 'platforms', 'fullname', 'contact', 'contact_email',
    'classifiers', 'download_url', 'provides', 'requires', 'obsoletes')

TEST_DATA = """# test file

line 3 \\
# intervening comment
  continues on next line
"""

UNIX_ID_SUPPORT = (grp and pwd)

UID_0_SUPPORT = (UNIX_ID_SUPPORT and sys.platform != 'cygwin')

MANIFEST = """# file GENERATED by distutils, do NOT edit
README
buildout.cfg
inroot.txt
setup.py
data%(sep)sdata.dt
scripts%(sep)sscript.py
some%(sep)sfile.txt
some%(sep)sother_file.txt
somecode%(sep)s__init__.py
somecode%(sep)sdoc.dat
somecode%(sep)sdoc.txt
"""

LANG_EXT = {'c': '.c', 'c++': '.cxx'}

PY39 = ((3, 9) < sys.version_info < (3, 10))

PYTHON_SOURCE_EXTENSION = """.py"""

HAS_USER_SITE = (True)

WINDOWS_SCHEME = {'purelib': '{base}/Lib/site-packages', 'platlib':
    '{base}/Lib/site-packages', 'headers': '{base}/Include/{dist_name}',
    'scripts': '{base}/Scripts', 'data': '{base}'}

PY37 = (sys.version_info < (3, 8))

TESTS_DATA_DIR = (Path(__file__).parent / 'data')

TRANSPARENT_FILE_TYPES = ['png', 'tiff']

PDFINFO_CONVERT_TO_INT = ['Pages']

DISTUTILS_FINDER = DistutilsMetaFinder()

PARSE_HTML = doctest.register_optionflag('PARSE_HTML')

PARSE_XML = doctest.register_optionflag('PARSE_XML')

NOPARSE_MARKUP = doctest.register_optionflag('NOPARSE_MARKUP')

XINCLUDE = """{http://www.w3.org/2001/XInclude}"""

XINCLUDE_INCLUDE = (XINCLUDE + 'include')

XINCLUDE_FALLBACK = (XINCLUDE + 'fallback')

XINCLUDE_ITER_TAG = (XINCLUDE + '*')

DEFAULT_MAX_INCLUSION_DEPTH = (6)

XML_SCHEMA_NS = """http://www.w3.org/2001/XMLSchema"""

RELAXNG_NS = """http://relaxng.org/ns/structure/1.0"""

SCHEMATRON_NS = """http://purl.oclc.org/dsdl/schematron"""

SVRL_NS = """http://purl.oclc.org/dsdl/svrl"""

ASSERTS_ONLY = svrl_validation_errors

ASSERTS_AND_REPORTS = _etree.XPath('//svrl:failed-assert | //svrl:successful-report', namespaces=
    {'svrl': SVRL_NS})

_DECLARATION_OR_DOCTYPE = Declaration

XHTML_NAMESPACE = """http://www.w3.org/1999/xhtml"""

ABBR = E.abbr

ACRONYM = E.acronym

ADDRESS = E.address

APPLET = E.applet

AREA = E.area

BASE = E.base

BASEFONT = E.basefont

BDO = E.bdo

BIG = """>"""

BLOCKQUOTE = E.blockquote

BODY = E.body

BR = E.br

BUTTON = E.button

CAPTION = E.caption

CENTER = E.center

CITE = E.cite

CODE = E.code

COL = E.col

COLGROUP = E.colgroup

DD = E.dd

DEL = getattr(E, 'del')

DFN = E.dfn

DIR = E.dir

DL = E.dl

DT = E.dt

EM = E.em

FIELDSET = E.fieldset

FONT = E.font

FORM = E.form

FRAME = E.frame

FRAMESET = E.frameset

HEAD = E.head

HR = E.hr

HTML = E.html

IFRAME = E.iframe

IMG = E.img

INS = E.ins

ISINDEX = E.isindex

KBD = E.kbd

LABEL = E.label

LEGEND = E.legend

LI = E.li

LINK = E.link

MAP = E.map

MENU = E.menu

META = E.meta

NOFRAMES = E.noframes

NOSCRIPT = E.noscript

OBJECT = E.object

OL = E.ol

OPTGROUP = E.optgroup

OPTION = E.option

PARAM = E.param

PRE = E.pre

SAMP = E.samp

SCRIPT = E.script

SELECT = E.select

SMALL = E.small

SPAN = E.span

STRIKE = E.strike

STRONG = E.strong

STYLE = E.style

SUP = E.sup

TABLE = E.table

TBODY = E.tbody

TD = E.td

TEXTAREA = E.textarea

TFOOT = E.tfoot

TH = E.th

THEAD = E.thead

TITLE = E.title

TR = E.tr

TT = E.tt

UL = E.ul

VAR = ['A1', 'A2']

ATTR = dict

LOGGER = logging.getLogger('pytesseract')

DEFAULT_ENCODING = """utf-8"""

LANG_PATTERN = re.compile('^[a-z_]+$')

RGB_MODE = """RGB"""

SUPPORTED_FORMATS = ('.xlsx', '.xlsm', '.xltx', '.xltm')

OSD_KEYS = {'Page number': ('page_num', int), 'Orientation in degrees': ('orientation',
    int), 'Rotate': ('rotate', int), 'Orientation confidence': (
    'orientation_conf', float), 'Script': ('script', str),
    'Script confidence': ('script_conf', float)}

EXTENTION_TO_CONFIG = {'box': 'tessedit_create_boxfile=1 batch.nochop makebox', 'xml':
    'tessedit_create_alto=1', 'hocr': 'tessedit_create_hocr=1', 'tsv':
    'tessedit_create_tsv=1'}

TESSERACT_MIN_VERSION = Version('3.05')

TESSERACT_ALTO_VERSION = Version('4.1.0')

BYTES = """bytes"""

DATAFRAME = """data.frame"""

DICT = """dict"""

BASE_PATH = os.path.join(os.path.dirname(__file__), 'tests')

TIMEZONES = [None, 'UTC', 'US/Eastern', 'Asia/Tokyo', 'dateutil/US/Pacific',
    'dateutil/Asia/Singapore', '+01:15', '-02:15', 'UTC+01:15', 'UTC-02:15',
    tzutc(), tzlocal(), FixedOffset(300), FixedOffset(0), FixedOffset(-300),
    timezone.utc, timezone(timedelta(hours=1)), timezone(timedelta(hours=-1
    ), name='foo')]

TIMEZONE_IDS = [repr(i) for i in TIMEZONES]

_UTCS = ['utc', 'dateutil/UTC', utc, tzutc(), timezone.utc]

TAG = """tag: """

GITS = ['git.cmd', 'git.exe']

IS64 = (sys.maxsize > 2 ** 32)

PY310 = (sys.version_info >= (3, 10))

PY311 = (sys.version_info >= (3, 11))

PY312 = (sys.version_info >= (3, 12))

PYPY = (platform.python_implementation() == 'PyPy')

ISMUSL = ('musl' in (sysconfig.get_config_var('HOST_GNU_TYPE') or ''))

REF_COUNT = (2 if PY311 else 3)

VERSIONS = {'adbc-driver-postgresql': '0.8.0', 'adbc-driver-sqlite': '0.8.0', 'bs4':
    '4.11.2', 'blosc': '1.21.3', 'bottleneck': '1.3.6',
    'dataframe-api-compat': '0.1.7', 'fastparquet': '2022.12.0', 'fsspec':
    '2022.11.0', 'html5lib': '1.1', 'hypothesis': '6.46.1', 'gcsfs':
    '2022.11.0', 'jinja2': '3.1.2', 'lxml.etree': '4.9.2', 'matplotlib':
    '3.6.3', 'numba': '0.56.4', 'numexpr': '2.8.4', 'odfpy': '1.4.1',
    'openpyxl': '3.1.0', 'pandas_gbq': '0.19.0', 'psycopg2': '2.9.6',
    'pymysql': '1.0.2', 'pyarrow': '10.0.1', 'pyreadstat': '1.2.0',
    'pytest': '7.3.2', 'python-calamine': '0.1.7', 'pyxlsb': '1.0.10',
    's3fs': '2022.11.0', 'scipy': '1.10.0', 'sqlalchemy': '2.0.0', 'tables':
    '3.8.0', 'tabulate': '0.9.0', 'xarray': '2022.12.0', 'xlrd': '2.0.1',
    'xlsxwriter': '3.0.5', 'zstandard': '0.19.0', 'tzdata': '2022.7',
    'qtpy': '2.3.0', 'pyqt5': '5.15.9'}

INSTALL_MAPPING = {'bs4': 'beautifulsoup4', 'bottleneck': 'Bottleneck', 'jinja2': 'Jinja2',
    'lxml.etree': 'lxml', 'odf': 'odfpy', 'pandas_gbq': 'pandas-gbq',
    'python_calamine': 'python-calamine', 'sqlalchemy': 'SQLAlchemy',
    'tables': 'pytables'}

ARGMINMAX_DEFAULTS = {'out': None}

LOGICAL_FUNC_DEFAULTS = {'out': None, 'keepdims': False}

MINMAX_DEFAULTS = {'axis': None, 'dtype': None, 'out': None, 'keepdims': False}

SUM_DEFAULTS = STAT_FUNC_DEFAULTS.copy()

PROD_DEFAULTS = SUM_DEFAULTS.copy()

MEAN_DEFAULTS = SUM_DEFAULTS.copy()

MEDIAN_DEFAULTS = STAT_FUNC_DEFAULTS.copy()

TRANSPOSE_DEFAULTS = {'axes': None}

RESAMPLER_NUMPY_OPS = ('min', 'max', 'sum', 'prod', 'mean', 'std', 'var')

_BOTTLENECK_INSTALLED = (bn is not None)

_USE_BOTTLENECK = v

NP_METHODS = ['linear', 'time', 'index', 'values']

SP_METHODS = ['nearest', 'zero', 'slinear', 'quadratic', 'cubic', 'barycentric', 'krogh',
    'spline', 'polynomial', 'from_derivatives', 'piecewise_polynomial',
    'pchip', 'akima', 'cubicspline']

_MINIMUM_COMP_ARR_LEN = (1000000)

REDUCTION_ALIASES = {'maximum': 'max', 'minimum': 'min', 'add': 'sum', 'multiply': 'prod'}

_AXIS_LEN = len(_AXIS_ORDERS)

K = self.nseries

_NS = slice(None, None)

GLOBAL_USE_NUMBA = enable

CPU = (1)

CUDA = (2)

CPU_PINNED = (3)

OPENCL = (4)

VULKAN = (7)

METAL = (8)

VPI = (9)

ROCM = (10)

INT = (0)

UINT = (1)

BOOL = """b"""

DATETIME = (22)

CATEGORICAL = (23)

NON_NULLABLE = (0)

USE_NAN = (1)

USE_SENTINEL = (2)

USE_BITMASK = (3)

USE_BYTEMASK = (4)

PYARROW_CTYPES = {'null': 'n', 'bool': 'b', 'uint8': 'C', 'uint16': 'S', 'uint32': 'I',
    'uint64': 'L', 'int8': 'c', 'int16': 'S', 'int32': 'i', 'int64': 'l',
    'halffloat': 'e', 'float': 'f', 'double': 'g', 'string': 'u',
    'large_string': 'U', 'binary': 'z', 'time32[s]': 'tts', 'time32[ms]':
    'ttm', 'time64[us]': 'ttu', 'time64[ns]': 'ttn', 'date32[day]': 'tdD',
    'date64[ms]': 'tdm', 'timestamp[s]': 'tss:', 'timestamp[ms]': 'tsm:',
    'timestamp[us]': 'tsu:', 'timestamp[ns]': 'tsn:', 'duration[s]': 'tDs',
    'duration[ms]': 'tDm', 'duration[us]': 'tDu', 'duration[ns]': 'tDn'}

NULL = """n"""

INT8 = """c"""

UINT8 = """C"""

INT16 = """s"""

UINT16 = """S"""

INT32 = """i"""

UINT32 = """I"""

INT64 = """l"""

UINT64 = """L"""

FLOAT16 = """e"""

FLOAT32 = """f"""

FLOAT64 = """g"""

LARGE_STRING = """U"""

DATE32 = """tdD"""

DATE64 = """tdm"""

TIMESTAMP = """ts{resolution}:{tz}"""

TIME = (True)

LITTLE = """<"""

NATIVE = """="""

NA = iNaT

_NP_KINDS = {'i': DtypeKind.INT, 'u': DtypeKind.UINT, 'f': DtypeKind.FLOAT, 'b':
    DtypeKind.BOOL, 'U': DtypeKind.STRING, 'M': DtypeKind.DATETIME, 'm':
    DtypeKind.DATETIME}

_NULL_DESCRIPTION = {DtypeKind.FLOAT: (ColumnNullType.USE_NAN, None), DtypeKind.DATETIME: (
    ColumnNullType.USE_SENTINEL, iNaT), DtypeKind.INT: (ColumnNullType.
    NON_NULLABLE, None), DtypeKind.UINT: (ColumnNullType.NON_NULLABLE, None
    ), DtypeKind.BOOL: (ColumnNullType.NON_NULLABLE, None), DtypeKind.
    CATEGORICAL: (ColumnNullType.USE_SENTINEL, -1), DtypeKind.STRING: (
    ColumnNullType.USE_BYTEMASK, 0)}

_NO_VALIDITY_BUFFER = {ColumnNullType.NON_NULLABLE: 'This column is non-nullable', ColumnNullType
    .USE_NAN: 'This column uses NaN as null', ColumnNullType.USE_SENTINEL:
    'This column uses a sentinel value'}

INF_AS_NA = (False)

DT64NS_DTYPE = conversion.DT64NS_DTYPE

TD64NS_DTYPE = conversion.TD64NS_DTYPE

INT64_DTYPE = np.dtype(np.int64)

COW_WARNING_GENERAL_MSG = """Setting a value on a view: behaviour will change in pandas 3.0.
You are mutating a Series or DataFrame object, and currently this mutation will
also have effect on other Series or DataFrame objects that share data with this
object. In pandas 3.0 (with Copy-on-Write), updating one Series or DataFrame object
will never modify another.
"""

COW_WARNING_SETITEM_MSG = """Setting a value on a view: behaviour will change in pandas 3.0.
Currently, the mutation will also have effect on the object that shares data
with this object. For example, when setting a value in a Series that was
extracted from a column of a DataFrame, that DataFrame will also be updated:

    ser = df["col"]
    ser[0] = 0     <--- in pandas 2, this also updates `df`

In pandas 3.0 (with Copy-on-Write), updating one Series/DataFrame will never
modify another, and thus in the example above, `df` will not be changed.
"""

BACKTICK_QUOTED_STRING = (100)

NUMEXPR_INSTALLED = (ne is not None)

USE_NUMEXPR = v

_ALLOWED_DTYPES = {'evaluate': {'int64', 'int32', 'float64', 'float32', 'bool'}, 'where': {
    'int64', 'float64', 'bool'}}

_MIN_ELEMENTS = (1000000)

_BOOL_OP_UNSUPPORTED = {'+': '|', '*': '&', '-': '^'}

_TEST_MODE = v

_TEST_RESULT = []

REDUCTIONS = ('sum', 'prod', 'min', 'max')

MATHOPS = (_unary_math_ops + _binary_math_ops)

LOCAL_TAG = """__pd_eval_local_"""

CMP_OPS_SYMS = ('>', '<', '>=', '<=', '==', '!=', 'in', 'not in')

BOOL_OPS_SYMS = ('&', '|', 'and', 'or')

ARITH_OPS_SYMS = ('+', '-', '*', '/', '**', '//', '%')

SPECIAL_CASE_ARITH_OPS_SYMS = ('**', '//', '%')

UNARY_OPS_SYMS = ('+', '-', '~', 'not')

_KT = TypeVar('_KT')

DEFAULT_GLOBALS = {'Timestamp': Timestamp, 'datetime': datetime.datetime, 'True': True,
    'False': False, 'list': list, 'tuple': tuple, 'inf': np.inf, 'Inf': np.inf}

PARSERS = {'python': PythonExprVisitor, 'pandas': PandasExprVisitor}

_ITER_CHUNKSIZE = (10000)

_TRUE_VALUES = {'True', 'TRUE', 'true', '1', '1.0'}

_FALSE_VALUES = {'False', 'FALSE', 'false', '0', '0.0'}

_ERROR_MSG = """Disallowed deserialization of 'arrow.py_extension_type':
storage_type = {storage_type}
serialized = {serialized}
pickle disassembly:
{pickle_disassembly}

Reading of untrusted Parquet or Feather files with a PyExtensionType column
allows arbitrary code execution.
If you trust this file, you can enable reading the extension type by one of:

- upgrading to pyarrow >= 14.0.1, and call `pa.PyExtensionType.set_auto_load(True)`
- install pyarrow-hotfix (`pip install pyarrow-hotfix`) and disable it by running
  `import pyarrow_hotfix; pyarrow_hotfix.uninstall()`

We strongly recommend updating your Parquet/Feather files to use extension types
derived from `pyarrow.ExtensionType` instead, and register this type explicitly.
"""

ARROW_CMP_FUNCS = {'eq': pc.equal, 'ne': pc.not_equal, 'lt': pc.less, 'gt': pc.greater, 'le':
    pc.less_equal, 'ge': pc.greater_equal}

ARROW_LOGICAL_FUNCS = {'and_': pc.and_kleene, 'rand_': lambda x, y: pc.and_kleene(y, x), 'or_':
    pc.or_kleene, 'ror_': lambda x, y: pc.or_kleene(y, x), 'xor': pc.xor,
    'rxor': lambda x, y: pc.xor(y, x)}

ARROW_BIT_WISE_FUNCS = {'and_': pc.bit_wise_and, 'rand_': lambda x, y: pc.bit_wise_and(y, x),
    'or_': pc.bit_wise_or, 'ror_': lambda x, y: pc.bit_wise_or(y, x), 'xor':
    pc.bit_wise_xor, 'rxor': lambda x, y: pc.bit_wise_xor(y, x)}

ARROW_ARITHMETIC_FUNCS = {'add': pc.add_checked, 'radd': lambda x, y: pc.add_checked(y, x), 'sub':
    pc.subtract_checked, 'rsub': lambda x, y: pc.subtract_checked(y, x),
    'mul': pc.multiply_checked, 'rmul': lambda x, y: pc.multiply_checked(y,
    x), 'truediv': lambda x, y: pc.divide(*cast_for_truediv(x, y)),
    'rtruediv': lambda x, y: pc.divide(*cast_for_truediv(y, x)), 'floordiv':
    lambda x, y: floordiv_compat(x, y), 'rfloordiv': lambda x, y:
    floordiv_compat(y, x), 'mod': NotImplemented, 'rmod': NotImplemented,
    'divmod': NotImplemented, 'rdivmod': NotImplemented, 'pow': pc.
    power_checked, 'rpow': lambda x, y: pc.power_checked(y, x)}

_BOOL_OP_NOT_ALLOWED = {operator.truediv, roperator.rtruediv, operator.floordiv, roperator.
    rfloordiv, operator.pow, roperator.rpow}

PKG = os.path.dirname(os.path.dirname(__file__))

_FORMAT_MAP = {'f': 'fixed', 'fixed': 'fixed', 't': 'table', 'table': 'table'}

_AXES_MAP = {DataFrame: [0]}

_STORER_MAP = {'series': SeriesFixed, 'frame': FrameFixed}

_TABLE_MAP = {'generic_table': GenericTable, 'appendable_series': AppendableSeriesTable,
    'appendable_multiseries': AppendableMultiSeriesTable,
    'appendable_frame': AppendableFrameTable, 'appendable_multiframe':
    AppendableMultiFrameTable, 'worm': WORMTable}

_RE_WHITESPACE = re.compile('[\\r\\n]+|\\s{2,}')

_VALID_URLS = set(uses_relative + uses_netloc + uses_params)

_RFC_3986_PATTERN = re.compile('^[A-Za-z][A-Za-z0-9+\\-+.]*://')

_SQL_TYPES = {'string': 'TEXT', 'floating': 'REAL', 'integer': 'INTEGER', 'datetime':
    'TIMESTAMP', 'date': 'DATE', 'time': 'TIME', 'boolean': 'INTEGER'}

MAX_DAY_DELTA = (Timestamp.max - datetime(1960, 1, 1)).days

MIN_DAY_DELTA = (Timestamp.min - datetime(1960, 1, 1)).days

MIN_MS_DELTA = (MIN_DAY_DELTA * 24 * 3600 * 1000)

MAX_MS_DELTA = (MAX_DAY_DELTA * 24 * 3600 * 1000)

NS_PER_DAY = (24 * 3600 * 1000 * 1000 * 1000)

US_PER_DAY = (NS_PER_DAY / 1000)

MANDATORY_DIALECT_ATTRS = ('delimiter', 'doublequote', 'escapechar', 'skipinitialspace', 'quotechar',
    'quoting')

_BOM = """﻿"""

SKIP = (2)

VALID_JUSTIFY_PARAMETERS = ('left', 'right', 'center', 'justify', 'justify-all', 'start', 'end',
    'inherit', 'match-parent', 'initial', 'unset')

ENG_PREFIXES = {(-24): 'y', (-21): 'z', (-18): 'a', (-15): 'f', (-12): 'p', (-9): 'n', (-6
    ): 'u', (-3): 'm', (0): '', (3): 'k', (6): 'M', (9): 'G', (12): 'T', (
    15): 'P', (18): 'E', (21): 'Z', (24): 'Y'}

NAMED_COLORS = CSS4_COLORS

VERTICAL_MAP = {'top': 'top', 'text-top': 'top', 'middle': 'center', 'baseline': 'bottom',
    'bottom': 'bottom', 'text-bottom': 'bottom'}

BOLD_MAP = {'bold': True, 'bolder': True, '600': True, '700': True, '800': True, '900':
    True, 'normal': False, 'lighter': False, '100': False, '200': False,
    '300': False, '400': False, '500': False}

ITALIC_MAP = {'normal': False, 'italic': True, 'oblique': True}

FAMILY_MAP = {'serif': 1, 'sans-serif': 2, 'cursive': 4, 'fantasy': 5}

BORDER_STYLE_MAP = {style.lower(): style for style in ['dashed', 'mediumDashDot', 'dashDotDot',
    'hair', 'dotted', 'mediumDashDotDot', 'double', 'dashDot',
    'slantDashDot', 'mediumDashed']}

IGNORED_WRAPPERS = ['toprule', 'midrule', 'bottomrule', 'column_format']

UNIT_RATIOS = {'pt': ('pt', 1), 'em': ('em', 1), 'rem': ('pt', 12), 'ex': ('em', 0.5),
    'px': ('pt', 0.75), 'pc': ('pt', 12), 'in': ('pt', 72), 'cm': ('in', 1 /
    2.54), 'mm': ('in', 1 / 25.4), 'q': ('mm', 0.25), '!!default': ('em', 0)}

FONT_SIZE_RATIOS = UNIT_RATIOS.copy()

MARGIN_RATIOS = UNIT_RATIOS.copy()

BORDER_WIDTH_RATIOS = UNIT_RATIOS.copy()

BORDER_STYLES = ['none', 'hidden', 'dotted', 'dashed', 'solid', 'double', 'groove', 'ridge',
    'inset', 'outset', 'mediumdashdot', 'dashdotdot', 'hair',
    'mediumdashdotdot', 'dashdot', 'slantdashdot', 'mediumdashed']

SIDE_SHORTHANDS = {(1): [0, 0, 0, 0], (2): [0, 1, 0, 1], (3): [0, 1, 2, 1], (4): [0, 1, 2, 3]}

SIDES = ('top', 'right', 'bottom', 'left')

CSS_EXPANSIONS = {**{(f'border-{prop}' if prop else 'border'): _border_expander(prop) for
    prop in ['', 'top', 'right', 'bottom', 'left']}, **{f'border-{prop}':
    _side_expander(f'border-{{:s}}-{prop}') for prop in ['color', 'style',
    'width']}, 'margin': _side_expander('margin-{:s}'), 'padding':
    _side_expander('padding-{:s}')}

CSS4_COLORS = {'aliceblue': 'F0F8FF', 'antiquewhite': 'FAEBD7', 'aqua': '00FFFF',
    'aquamarine': '7FFFD4', 'azure': 'F0FFFF', 'beige': 'F5F5DC', 'bisque':
    'FFE4C4', 'black': '000000', 'blanchedalmond': 'FFEBCD', 'blue':
    '0000FF', 'blueviolet': '8A2BE2', 'brown': 'A52A2A', 'burlywood':
    'DEB887', 'cadetblue': '5F9EA0', 'chartreuse': '7FFF00', 'chocolate':
    'D2691E', 'coral': 'FF7F50', 'cornflowerblue': '6495ED', 'cornsilk':
    'FFF8DC', 'crimson': 'DC143C', 'cyan': '00FFFF', 'darkblue': '00008B',
    'darkcyan': '008B8B', 'darkgoldenrod': 'B8860B', 'darkgray': 'A9A9A9',
    'darkgreen': '006400', 'darkgrey': 'A9A9A9', 'darkkhaki': 'BDB76B',
    'darkmagenta': '8B008B', 'darkolivegreen': '556B2F', 'darkorange':
    'FF8C00', 'darkorchid': '9932CC', 'darkred': '8B0000', 'darksalmon':
    'E9967A', 'darkseagreen': '8FBC8F', 'darkslateblue': '483D8B',
    'darkslategray': '2F4F4F', 'darkslategrey': '2F4F4F', 'darkturquoise':
    '00CED1', 'darkviolet': '9400D3', 'deeppink': 'FF1493', 'deepskyblue':
    '00BFFF', 'dimgray': '696969', 'dimgrey': '696969', 'dodgerblue':
    '1E90FF', 'firebrick': 'B22222', 'floralwhite': 'FFFAF0', 'forestgreen':
    '228B22', 'fuchsia': 'FF00FF', 'gainsboro': 'DCDCDC', 'ghostwhite':
    'F8F8FF', 'gold': 'FFD700', 'goldenrod': 'DAA520', 'gray': '808080',
    'green': '008000', 'greenyellow': 'ADFF2F', 'grey': '808080',
    'honeydew': 'F0FFF0', 'hotpink': 'FF69B4', 'indianred': 'CD5C5C',
    'indigo': '4B0082', 'ivory': 'FFFFF0', 'khaki': 'F0E68C', 'lavender':
    'E6E6FA', 'lavenderblush': 'FFF0F5', 'lawngreen': '7CFC00',
    'lemonchiffon': 'FFFACD', 'lightblue': 'ADD8E6', 'lightcoral': 'F08080',
    'lightcyan': 'E0FFFF', 'lightgoldenrodyellow': 'FAFAD2', 'lightgray':
    'D3D3D3', 'lightgreen': '90EE90', 'lightgrey': 'D3D3D3', 'lightpink':
    'FFB6C1', 'lightsalmon': 'FFA07A', 'lightseagreen': '20B2AA',
    'lightskyblue': '87CEFA', 'lightslategray': '778899', 'lightslategrey':
    '778899', 'lightsteelblue': 'B0C4DE', 'lightyellow': 'FFFFE0', 'lime':
    '00FF00', 'limegreen': '32CD32', 'linen': 'FAF0E6', 'magenta': 'FF00FF',
    'maroon': '800000', 'mediumaquamarine': '66CDAA', 'mediumblue':
    '0000CD', 'mediumorchid': 'BA55D3', 'mediumpurple': '9370DB',
    'mediumseagreen': '3CB371', 'mediumslateblue': '7B68EE',
    'mediumspringgreen': '00FA9A', 'mediumturquoise': '48D1CC',
    'mediumvioletred': 'C71585', 'midnightblue': '191970', 'mintcream':
    'F5FFFA', 'mistyrose': 'FFE4E1', 'moccasin': 'FFE4B5', 'navajowhite':
    'FFDEAD', 'navy': '000080', 'oldlace': 'FDF5E6', 'olive': '808000',
    'olivedrab': '6B8E23', 'orange': 'FFA500', 'orangered': 'FF4500',
    'orchid': 'DA70D6', 'palegoldenrod': 'EEE8AA', 'palegreen': '98FB98',
    'paleturquoise': 'AFEEEE', 'palevioletred': 'DB7093', 'papayawhip':
    'FFEFD5', 'peachpuff': 'FFDAB9', 'peru': 'CD853F', 'pink': 'FFC0CB',
    'plum': 'DDA0DD', 'powderblue': 'B0E0E6', 'purple': '800080',
    'rebeccapurple': '663399', 'red': 'FF0000', 'rosybrown': 'BC8F8F',
    'royalblue': '4169E1', 'saddlebrown': '8B4513', 'salmon': 'FA8072',
    'sandybrown': 'F4A460', 'seagreen': '2E8B57', 'seashell': 'FFF5EE',
    'sienna': 'A0522D', 'silver': 'C0C0C0', 'skyblue': '87CEEB',
    'slateblue': '6A5ACD', 'slategray': '708090', 'slategrey': '708090',
    'snow': 'FFFAFA', 'springgreen': '00FF7F', 'steelblue': '4682B4', 'tan':
    'D2B48C', 'teal': '008080', 'thistle': 'D8BFD8', 'tomato': 'FF6347',
    'turquoise': '40E0D0', 'violet': 'EE82EE', 'wheat': 'F5DEB3', 'white':
    'FFFFFF', 'whitesmoke': 'F5F5F5', 'yellow': 'FFFF00', 'yellowgreen':
    '9ACD32'}

_DEFAULT_CHUNKSIZE_CELLS = (100000)

INFO_DOCSTRING = dedent(
    """
    Print a concise summary of a {klass}.

    This method prints information about a {klass} including
    the index dtype{type_sub}, non-null values and memory usage.
    {version_added_sub}
    Parameters
    ----------
    verbose : bool, optional
        Whether to print the full summary. By default, the setting in
        ``pandas.options.display.max_info_columns`` is followed.
    buf : writable buffer, defaults to sys.stdout
        Where to send the output. By default, the output is printed to
        sys.stdout. Pass a writable buffer if you need to further process
        the output.
    {max_cols_sub}
    memory_usage : bool, str, optional
        Specifies whether total memory usage of the {klass}
        elements (including the index) should be displayed. By default,
        this follows the ``pandas.options.display.memory_usage`` setting.

        True always show memory usage. False never shows memory usage.
        A value of 'deep' is equivalent to "True with deep introspection".
        Memory usage is shown in human-readable units (base-2
        representation). Without deep introspection a memory estimation is
        made based in column dtype and number of rows assuming values
        consume the same memory amount for corresponding dtypes. With deep
        memory introspection, a real memory usage calculation is performed
        at the cost of computational resources. See the
        :ref:`Frequently Asked Questions <df-memory-usage>` for more
        details.
    {show_counts_sub}

    Returns
    -------
    None
        This method prints a summary of a {klass} and returns None.

    See Also
    --------
    {see_also_sub}

    Examples
    --------
    {examples_sub}
    """
    )

XLS_SIGNATURES = (b'\t\x00\x04\x00\x07\x00\x10\x00', b'\t\x02\x06\x00\x00\x00\x10\x00',
    b'\t\x04\x06\x00\x00\x00\x10\x00', b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1')

ZIP_SIGNATURE = b'PK\x03\x04'

PEEK_SIZE = max(map(len, XLS_SIGNATURES + (ZIP_SIGNATURE,)))

_STAMP_UNITS = ('s', 'ms', 'us', 'ns')

_MIN_STAMPS = {'s': 31536000, 'ms': 31536000000, 'us': 31536000000000, 'ns': 
    31536000000000000}

TABLE_SCHEMA_VERSION = """1.4.0"""

HAS_DISPLAY = os.getenv('DISPLAY')

EXCEPT_MSG = """
    Pyperclip could not find a copy/paste mechanism for your system.
    For more information, please visit
    https://pyperclip.readthedocs.io/en/latest/index.html#not-implemented-error
    """

DEFAULT_SELECTION = """-b"""

PRIMARY_SELECTION = """-p"""

GMEM_MOVEABLE = (2)

CF_UNICODETEXT = (13)

NAN1 = struct.unpack('d', struct.pack('=Q', 9221120237041090560))[0]

NAN2 = struct.unpack('d', struct.pack('=Q', 9221120237041090561))[0]

RANDS_CHARS = np.array(list(string.ascii_letters + string.digits), dtype=(np.str_, 1))

SLC = IndexSlice

NA_SENTINEL = (-1234567)

PARSING_ERR_MSG = """You might want to try:\\n    - passing `format` if your strings have a consistent format;\\n    - passing `format=\\'ISO8601\\'` if your strings are all ISO8601 but not necessarily in exactly the same format;\\n    - passing `format=\\'mixed\\'`, and the format will be inferred for each element individually. You might want to use `dayfirst` alongside this."""

DATE_RANGE = (date_range, 'dti', datetime(2005, 1, 1), datetime(2005, 1, 10))

PERIOD_RANGE = (period_range, 'pi', datetime(2005, 1, 1), datetime(2005, 1, 10))

TIMEDELTA_RANGE = (timedelta_range, 'tdi', '1 day', '10 day')

NESTED_CASES = [(np.array([np.array([50, 70, 90]), np.array([20, 30])], dtype=object), np.
    array([np.array([50, 70, 90]), np.array([20, 30])], dtype=object)), (np
    .array([np.array([np.array([50, 70]), np.array([90])], dtype=object),
    np.array([np.array([20, 30])], dtype=object)], dtype=object), np.array(
    [np.array([np.array([50, 70]), np.array([90])], dtype=object), np.array
    ([np.array([20, 30])], dtype=object)], dtype=object)), (np.array([[50, 
    70, 90], [20, 30]], dtype=object), np.array([[50, 70, 90], [20, 30]],
    dtype=object)), (np.array([np.array([1, 2, 3]), np.array([4, 5])],
    dtype=object), np.array([[1, 2, 3], [4, 5]], dtype=object)), (np.array(
    [np.array([np.array([1, 2, 3]), np.array([4, 5])], dtype=object), np.
    array([np.array([6]), np.array([7, 8]), np.array([9])], dtype=object)],
    dtype=object), np.array([[[1, 2, 3], [4, 5]], [[6], [7, 8], [9]]],
    dtype=object)), (np.array([subarr, None], dtype=object), np.array([[[
    None, 'b'], ['c', 'd']], None], dtype=object)), (np.array([{'f1': 1,
    'f2': np.array(['a', 'b'], dtype=object)}], dtype=object), np.array([{
    'f1': 1, 'f2': np.array(['a', 'b'], dtype=object)}], dtype=object)), (
    np.array([{'f1': 1, 'f2': np.array(['a', 'b'], dtype=object)}], dtype=
    object), np.array([{'f1': 1, 'f2': ['a', 'b']}], dtype=object)), (np.
    array([np.array([{'f1': 1, 'f2': np.array(['a', 'b'], dtype=object)}],
    dtype=object), np.array([], dtype=object)], dtype=object), np.array([[{
    'f1': 1, 'f2': ['a', 'b']}], []], dtype=object))]

_HAVE_PYARROW = (False)

_HAVE_FASTPARQUET = (False)

_NA_VALUES = {'-1.#IND', '1.#QNAN', '1.#IND', '-1.#QNAN', '#N/A', 'N/A', 'n/a', 'NA',
    '<NA>', '#NA', 'NULL', 'null', 'NaN', 'nan', '-NaN', '-nan', '#N/A N/A',
    '', 'None'}

ARR_LEN = (100)

COLUMNS = ['foo', 'bar']

DF = DF.unstack(['VAR', 'TYP'])

_WEDNESDAY = datetime(2014, 4, 9)

_THURSDAY = datetime(2014, 4, 10)

_FRIDAY = datetime(2014, 4, 11)

_SATURDAY = datetime(2014, 4, 12)

_SUNDAY = datetime(2014, 4, 13)

_MONDAY = datetime(2014, 4, 14)

_TUESDAY = datetime(2014, 4, 15)

_NEXT_WEDNESDAY = datetime(2014, 4, 16)

JNJ = [datetime(2005, 1, 2), datetime(2006, 1, 1), datetime(2006, 12, 31),
    datetime(2007, 12, 30), datetime(2008, 12, 28), datetime(2010, 1, 3),
    datetime(2011, 1, 2), datetime(2012, 1, 1), datetime(2012, 12, 30)]

DEC_SAT = FY5253(n=-1, startingMonth=12, weekday=5, variation='nearest')

GMCR = [datetime(2010, 3, 27), datetime(2010, 6, 26), datetime(2010, 9, 25),
    datetime(2010, 12, 25), datetime(2011, 3, 26), datetime(2011, 6, 25),
    datetime(2011, 9, 24), datetime(2011, 12, 24), datetime(2012, 3, 24),
    datetime(2012, 6, 23), datetime(2012, 9, 29), datetime(2012, 12, 29),
    datetime(2013, 3, 30), datetime(2013, 6, 29)]

MU = [datetime(2012, 5, 31), datetime(2012, 8, 30), datetime(2012, 11, 29),
    datetime(2013, 2, 28), datetime(2013, 5, 30)]

MON = (0)

TUE = (1)

WED = (2)

THU = (3)

FRI = (4)

SAT = (5)

SUN = (6)

_ARITHMETIC_DATE_OFFSET = ['years', 'months', 'weeks', 'days', 'hours', 'minutes', 'seconds',
    'milliseconds', 'microseconds']

MIXED_FLOAT_DTYPES = ['float16', 'float32', 'float64']

MIXED_INT_DTYPES = ['uint8', 'uint16', 'uint32', 'uint64', 'int8', 'int16', 'int32', 'int64']

NUM_ROWS = (100)

PAE = ['ITA', 'FRA']

TYP = ['CRT', 'DBT', 'NET']

MI = MultiIndex.from_product([PAE, VAR, TYP], names=['PAE', 'VAR', 'TYP'])

FLOAT_TYPES = list(np.typecodes['AllFloat'])

SHUFFLED = [4, 6, 7, 2, 1, 0, 5, 3]

MANAGERS = [create_single_mgr('f8', N), create_single_mgr('i8', N), create_mgr(
    'a,b,c,d,e,f: f8', item_shape=(N,)), create_mgr('a,b,c,d,e,f: i8',
    item_shape=(N,)), create_mgr('a,b: f8; c,d: i8; e,f: string',
    item_shape=(N,)), create_mgr('a,b: f8; c,d: i8; e,f: f8', item_shape=(N,))]

MIN = arr[0]

MAX = arr[-1]

EXTREME_VALUES = [0, 123456789, None, iNaT, 2 ** 63 - 1, -2 ** 63 + 1]

FINE_TO_COARSE_SAFE = [123000000000, None, -123000000000]

COARSE_TO_FINE_SAFE = [123, None, -123]

EXPECTED_SINGLE_ROW_RESULTS = [([1, 2, 3], [np.nan, 2, 3], FutureWarning), ([1.0, 2.0, 3.0], [np.nan, 2.0,
    3.0], None), ([datetime(2000, 1, 1), datetime(2000, 1, 2), datetime(
    2000, 1, 3)], [NaT, datetime(2000, 1, 2), datetime(2000, 1, 3)], None),
    (['foo', 'bar', 'baz'], [None, 'bar', 'baz'], None)]

NUM_COLS = (10)

X1 = """x1"""

OPTIONAL_INTS = st.lists(st.one_of(st.integers(), st.none()), max_size=10, min_size=3)

OPTIONAL_FLOATS = st.lists(st.one_of(st.floats(), st.none()), max_size=10, min_size=3)

OPTIONAL_TEXT = st.lists(st.one_of(st.none(), st.text()), max_size=10, min_size=3)

OPTIONAL_DICTS = st.lists(st.one_of(st.none(), st.dictionaries(st.text(), st.integers())),
    max_size=10, min_size=3)

OPTIONAL_LISTS = st.lists(st.one_of(st.none(), st.lists(st.text(), max_size=10, min_size=3)),
    max_size=10, min_size=3)

OPTIONAL_ONE_OF_ALL = st.one_of(OPTIONAL_DICTS, OPTIONAL_FLOATS, OPTIONAL_INTS, OPTIONAL_LISTS,
    OPTIONAL_TEXT)

DATETIME_NO_TZ = st.datetimes()

DATETIME_JAN_1_1900_OPTIONAL_TZ = st.datetimes(min_value=pd.Timestamp(1900, 1, 1).to_pydatetime(), max_value=
    pd.Timestamp(1900, 1, 1).to_pydatetime(), timezones=st.one_of(st.none(),
    dateutil_timezones(), pytz_timezones()))

DATETIME_IN_PD_TIMESTAMP_RANGE_NO_TZ = st.datetimes(min_value=pd.Timestamp.min.to_pydatetime(warn=False),
    max_value=pd.Timestamp.max.to_pydatetime(warn=False))

INT_NEG_999_TO_POS_999 = st.integers(-999, 999)

YQM_OFFSET = st.one_of(*map(st.from_type, [MonthBegin, MonthEnd, BMonthBegin, BMonthEnd,
    QuarterBegin, QuarterEnd, BQuarterBegin, BQuarterEnd, YearBegin,
    YearEnd, BYearBegin, BYearEnd]))

ALL_INT_NUMPY_DTYPES = (UNSIGNED_INT_NUMPY_DTYPES + SIGNED_INT_NUMPY_DTYPES)

ALL_INT_EA_DTYPES = (UNSIGNED_INT_EA_DTYPES + SIGNED_INT_EA_DTYPES)

ALL_REAL_NUMPY_DTYPES = (FLOAT_NUMPY_DTYPES + ALL_INT_NUMPY_DTYPES)

ALL_REAL_EXTENSION_DTYPES = (FLOAT_EA_DTYPES + ALL_INT_EA_DTYPES)

ALL_NUMPY_DTYPES = (ALL_REAL_NUMPY_DTYPES + COMPLEX_DTYPES + STRING_DTYPES + DATETIME64_DTYPES +
    TIMEDELTA64_DTYPES + BOOL_DTYPES + OBJECT_DTYPES + BYTES_DTYPES)

NARROW_NP_DTYPES = [np.float16, np.float32, np.int8, np.int16, np.int32, np.uint8, np.uint16,
    np.uint32]

PYTHON_DATA_TYPES = [str, int, float, complex, list, tuple, range, dict, set, frozenset, bool,
    bytes, bytearray, memoryview]

ENDIAN = {'little': '<', 'big': '>'}[byteorder]

NULL_OBJECTS = [None, np.nan, pd.NaT, float('nan'), pd.NA, Decimal('NaN')]

NP_NAT_OBJECTS = [cls('NaT', unit) for cls in [np.datetime64, np.timedelta64] for unit in [
    'Y', 'M', 'W', 'D', 'h', 'm', 's', 'ms', 'us', 'ns', 'ps', 'fs', 'as']]

UNSIGNED_INT_PYARROW_DTYPES = [pa.uint8(), pa.uint16(), pa.uint32(), pa.uint64()]

SIGNED_INT_PYARROW_DTYPES = [pa.int8(), pa.int16(), pa.int32(), pa.int64()]

ALL_INT_PYARROW_DTYPES = (UNSIGNED_INT_PYARROW_DTYPES + SIGNED_INT_PYARROW_DTYPES)

ALL_INT_PYARROW_DTYPES_STR_REPR = []

FLOAT_PYARROW_DTYPES = [pa.float32(), pa.float64()]

FLOAT_PYARROW_DTYPES_STR_REPR = []

DECIMAL_PYARROW_DTYPES = [pa.decimal128(7, 3)]

STRING_PYARROW_DTYPES = [pa.string()]

BINARY_PYARROW_DTYPES = [pa.binary()]

TIME_PYARROW_DTYPES = [pa.time32('s'), pa.time32('ms'), pa.time64('us'), pa.time64('ns')]

DATE_PYARROW_DTYPES = [pa.date32(), pa.date64()]

DATETIME_PYARROW_DTYPES = [pa.timestamp(unit=unit, tz=tz) for unit in ['s', 'ms', 'us', 'ns'] for tz in
    [None, 'UTC', 'US/Pacific', 'US/Eastern']]

TIMEDELTA_PYARROW_DTYPES = [pa.duration(unit) for unit in ['s', 'ms', 'us', 'ns']]

BOOL_PYARROW_DTYPES = [pa.bool_()]

ALL_PYARROW_DTYPES = []

ALL_REAL_PYARROW_DTYPES_STR_REPR = []

ALL_REAL_NULLABLE_DTYPES = (FLOAT_NUMPY_DTYPES + ALL_REAL_EXTENSION_DTYPES +
    ALL_REAL_PYARROW_DTYPES_STR_REPR)

_UNITS = ['s', 'ms', 'us', 'ns']

_BUILTIN_DIALECTS = {'excel', 'excel-tab', 'unix'}

_ALIASES = {'x_compat': 'xaxis.compat'}

_DEFAULT_KEYS = ['xaxis.compat']

UNIT = (1.0 / (24 * 3600 * 1000))

M366MASK = tuple([1] * 31 + [2] * 29 + [3] * 31 + [4] * 30 + [5] * 31 + [6] * 30 + [7] *
    31 + [8] * 31 + [9] * 30 + [10] * 31 + [11] * 30 + [12] * 31 + [1] * 7)

M365MASK = tuple(M365MASK)

MDAY366MASK = tuple(M31 + M29 + M31 + M30 + M31 + M30 + M31 + M31 + M30 + M31 + M30 + M31 +
    M31[:7])

MDAY365MASK = tuple(MDAY365MASK)

NMDAY366MASK = tuple(M31 + M29 + M31 + M30 + M31 + M30 + M31 + M31 + M30 + M31 + M30 + M31 +
    M31[:7])

NMDAY365MASK = list(NMDAY366MASK)

M366RANGE = (0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335, 366)

M365RANGE = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365)

WDAYMASK = ([0, 1, 2, 3, 4, 5, 6] * 55)

FREQNAMES = ['YEARLY', 'MONTHLY', 'WEEKLY', 'DAILY', 'HOURLY', 'MINUTELY', 'SECONDLY']

TZID = tzlookup(tzkey)

TZID_NAMES = dict(map(lambda x: (x.upper(), x), re.findall('TZID=(?P<name>[^:]+):', s)))

EASTER_JULIAN = (1)

EASTER_ORTHODOX = (2)

EASTER_WESTERN = (3)

ZONEFILENAME = """dateutil-zoneinfo.tar.gz"""

METADATA_FN = """METADATA"""

_CLASS_ZONE_INSTANCE = []

_DATE_SEP = b'-'

_TIME_SEP = b':'

_FRACTION_REGEX = re.compile(b'[\\.,]([0-9]+)')

DEFAULT_ISOPARSER = isoparser()

JUMP = [' ', '.', ',', ';', '-', '/', "'", 'at', 'on', 'and', 'ad', 'm', 't', 'of',
    'st', 'nd', 'rd', 'th']

WEEKDAYS = [('Mon', 'Monday'), ('Tue', 'Tuesday'), ('Wed', 'Wednesday'), ('Thu',
    'Thursday'), ('Fri', 'Friday'), ('Sat', 'Saturday'), ('Sun', 'Sunday')]

MONTHS = [('Jan', 'January'), ('Feb', 'February'), ('Mar', 'March'), ('Apr', 'April'
    ), ('May', 'May'), ('Jun', 'June'), ('Jul', 'July'), ('Aug', 'August'),
    ('Sep', 'Sept', 'September'), ('Oct', 'October'), ('Nov', 'November'),
    ('Dec', 'December')]

HMS = [('h', 'hour', 'hours'), ('m', 'minute', 'minutes'), ('s', 'second', 'seconds')
    ]

AMPM = [('am', 'a'), ('pm', 'p')]

UTCZONE = ['UTC', 'GMT', 'Z', 'z']

PERTAIN = ['of']

TZOFFSET = {}

DEFAULTPARSER = parser()

DEFAULTTZPARSER = _tzparser()

EPOCH = datetime.datetime(1970, 1, 1, 0, 0)

EPOCHORDINAL = EPOCH.toordinal()

TZFILES = []

TZPATHS = []

ONEWEEK = datetime.timedelta(7)

TZKEYNAMENT = """SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Time Zones"""

TZKEYNAME9X = """SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Time Zones"""

TZLOCALKEYNAME = """SYSTEM\\CurrentControlSet\\Control\\TimeZoneInformation"""

TZKEYNAME = _settzkeyname()

KEEP_VBA = (False)

STRING_TAG = ('{%s}si' % SHEET_MAIN_NS)

CLASS_MAPPING = {StringProperty: 'lpwstr', IntProperty: 'i4', FloatProperty: 'r8',
    DateTimeProperty: 'filetime', BoolProperty: 'bool', LinkProperty:
    'linkTarget'}

XML_MAPPING = {v: k for k, v in CLASS_MAPPING.items()}

DEFAULT_TYPES = [FileExtension('rels',
    'application/vnd.openxmlformats-package.relationships+xml'),
    FileExtension('xml', 'application/xml')]

DEFAULT_OVERRIDE = [Override('/' + ARC_STYLE, STYLES_TYPE), Override('/' + ARC_THEME,
    THEME_TYPE), Override('/docProps/core.xml',
    'application/vnd.openxmlformats-package.core-properties+xml'), Override
    ('/docProps/app.xml',
    'application/vnd.openxmlformats-officedocument.extended-properties+xml')]

PRESET_COLORS = ['aliceBlue', 'antiqueWhite', 'aqua', 'aquamarine', 'azure', 'beige',
    'bisque', 'black', 'blanchedAlmond', 'blue', 'blueViolet', 'brown',
    'burlyWood', 'cadetBlue', 'chartreuse', 'chocolate', 'coral',
    'cornflowerBlue', 'cornsilk', 'crimson', 'cyan', 'darkBlue', 'darkCyan',
    'darkGoldenrod', 'darkGray', 'darkGrey', 'darkGreen', 'darkKhaki',
    'darkMagenta', 'darkOliveGreen', 'darkOrange', 'darkOrchid', 'darkRed',
    'darkSalmon', 'darkSeaGreen', 'darkSlateBlue', 'darkSlateGray',
    'darkSlateGrey', 'darkTurquoise', 'darkViolet', 'dkBlue', 'dkCyan',
    'dkGoldenrod', 'dkGray', 'dkGrey', 'dkGreen', 'dkKhaki', 'dkMagenta',
    'dkOliveGreen', 'dkOrange', 'dkOrchid', 'dkRed', 'dkSalmon',
    'dkSeaGreen', 'dkSlateBlue', 'dkSlateGray', 'dkSlateGrey',
    'dkTurquoise', 'dkViolet', 'deepPink', 'deepSkyBlue', 'dimGray',
    'dimGrey', 'dodgerBlue', 'firebrick', 'floralWhite', 'forestGreen',
    'fuchsia', 'gainsboro', 'ghostWhite', 'gold', 'goldenrod', 'gray',
    'grey', 'green', 'greenYellow', 'honeydew', 'hotPink', 'indianRed',
    'indigo', 'ivory', 'khaki', 'lavender', 'lavenderBlush', 'lawnGreen',
    'lemonChiffon', 'lightBlue', 'lightCoral', 'lightCyan',
    'lightGoldenrodYellow', 'lightGray', 'lightGrey', 'lightGreen',
    'lightPink', 'lightSalmon', 'lightSeaGreen', 'lightSkyBlue',
    'lightSlateGray', 'lightSlateGrey', 'lightSteelBlue', 'lightYellow',
    'ltBlue', 'ltCoral', 'ltCyan', 'ltGoldenrodYellow', 'ltGray', 'ltGrey',
    'ltGreen', 'ltPink', 'ltSalmon', 'ltSeaGreen', 'ltSkyBlue',
    'ltSlateGray', 'ltSlateGrey', 'ltSteelBlue', 'ltYellow', 'lime',
    'limeGreen', 'linen', 'magenta', 'maroon', 'medAquamarine', 'medBlue',
    'medOrchid', 'medPurple', 'medSeaGreen', 'medSlateBlue',
    'medSpringGreen', 'medTurquoise', 'medVioletRed', 'mediumAquamarine',
    'mediumBlue', 'mediumOrchid', 'mediumPurple', 'mediumSeaGreen',
    'mediumSlateBlue', 'mediumSpringGreen', 'mediumTurquoise',
    'mediumVioletRed', 'midnightBlue', 'mintCream', 'mistyRose', 'moccasin',
    'navajoWhite', 'navy', 'oldLace', 'olive', 'oliveDrab', 'orange',
    'orangeRed', 'orchid', 'paleGoldenrod', 'paleGreen', 'paleTurquoise',
    'paleVioletRed', 'papayaWhip', 'peachPuff', 'peru', 'pink', 'plum',
    'powderBlue', 'purple', 'red', 'rosyBrown', 'royalBlue', 'saddleBrown',
    'salmon', 'sandyBrown', 'seaGreen', 'seaShell', 'sienna', 'silver',
    'skyBlue', 'slateBlue', 'slateGray', 'slateGrey', 'snow', 'springGreen',
    'steelBlue', 'tan', 'teal', 'thistle', 'tomato', 'turquoise', 'violet',
    'wheat', 'white', 'whiteSmoke', 'yellow', 'yellowGreen']

SCHEME_COLORS = ['bg1', 'tx1', 'bg2', 'tx2', 'accent1', 'accent2', 'accent3', 'accent4',
    'accent5', 'accent6', 'hlink', 'folHlink', 'phClr', 'dk1', 'lt1', 'dk2',
    'lt2']

_COLOR_SET = ('dk1', 'lt1', 'dk2', 'lt2', 'accent1', 'accent2', 'accent3', 'accent4',
    'accent5', 'accent6', 'hlink', 'folHlink')

NUMERIC_TYPES = (NUMERIC_TYPES + (numpy.short, numpy.ushort, numpy.intc, numpy.uintc, numpy
    .int_, numpy.uint, numpy.longlong, numpy.ulonglong, numpy.half, numpy.
    float16, numpy.single, numpy.double, numpy.longdouble, numpy.int8,
    numpy.int16, numpy.int32, numpy.int64, numpy.uint8, numpy.uint16, numpy
    .uint32, numpy.uint64, numpy.intp, numpy.uintp, numpy.float32, numpy.
    float64, numpy.bool_, numpy.floating, numpy.integer))

NUMPY = (False)

VER = sys.version_info

ABC = ABCMeta('ABC', (object,), {})

COL_RANGE = """[A-Z]{1,3}:[A-Z]{1,3}:"""

COL_RANGE_RE = re.compile('(\\$?[A-Za-z]{1,3}):(\\$?[A-Za-z]{1,3})$')

ROW_RANGE = """\\d+:\\d+:"""

ROW_RANGE_RE = re.compile('(\\$?[1-9][0-9]{0,6}):(\\$?[1-9][0-9]{0,6})$')

TITLES_REGEX = re.compile('{0}{1}?,?{2}?,?'.format(SHEET_TITLE, ROW_RANGE, COL_RANGE), re.
    VERBOSE)

PRINT_AREA_RE = re.compile(f'({SHEET_TITLE})?(?P<cells>{RANGE_EXPR})', re.VERBOSE)

ALL_TEMP_FILES = []

CELL_TAG = ('{%s}c' % SHEET_MAIN_NS)

VALUE_TAG = ('{%s}v' % SHEET_MAIN_NS)

FORMULA_TAG = ('{%s}f' % SHEET_MAIN_NS)

MERGE_TAG = ('{%s}mergeCells' % SHEET_MAIN_NS)

INLINE_STRING = ('{%s}is' % SHEET_MAIN_NS)

COL_TAG = ('{%s}col' % SHEET_MAIN_NS)

ROW_TAG = ('{%s}row' % SHEET_MAIN_NS)

CF_TAG = ('{%s}conditionalFormatting' % SHEET_MAIN_NS)

LEGACY_TAG = ('{%s}legacyDrawing' % SHEET_MAIN_NS)

PROT_TAG = ('{%s}sheetProtection' % SHEET_MAIN_NS)

EXT_TAG = ('{%s}extLst' % SHEET_MAIN_NS)

HYPERLINK_TAG = ('{%s}hyperlinks' % SHEET_MAIN_NS)

TABLE_TAG = ('{%s}tableParts' % SHEET_MAIN_NS)

PRINT_TAG = ('{%s}printOptions' % SHEET_MAIN_NS)

MARGINS_TAG = ('{%s}pageMargins' % SHEET_MAIN_NS)

PAGE_TAG = ('{%s}pageSetup' % SHEET_MAIN_NS)

HEADER_TAG = ('{%s}headerFooter' % SHEET_MAIN_NS)

FILTER_TAG = ('{%s}autoFilter' % SHEET_MAIN_NS)

VALIDATION_TAG = ('{%s}dataValidations' % SHEET_MAIN_NS)

PROPERTIES_TAG = ('{%s}sheetPr' % SHEET_MAIN_NS)

VIEWS_TAG = ('{%s}sheetViews' % SHEET_MAIN_NS)

FORMAT_TAG = ('{%s}sheetFormatPr' % SHEET_MAIN_NS)

ROW_BREAK_TAG = ('{%s}rowBreaks' % SHEET_MAIN_NS)

COL_BREAK_TAG = ('{%s}colBreaks' % SHEET_MAIN_NS)

SCENARIOS_TAG = ('{%s}scenarios' % SHEET_MAIN_NS)

DATA_TAG = ('{%s}sheetData' % SHEET_MAIN_NS)

DIMENSION_TAG = ('{%s}dimension' % SHEET_MAIN_NS)

CUSTOM_VIEWS_TAG = ('{%s}customSheetViews' % SHEET_MAIN_NS)

BREAK_NONE = (0)

BREAK_ROW = (1)

BREAK_COLUMN = (2)

SHEETSTATE_VISIBLE = """visible"""

SHEETSTATE_HIDDEN = """hidden"""

SHEETSTATE_VERYHIDDEN = """veryHidden"""

PAPERSIZE_LETTER = """1"""

PAPERSIZE_LETTER_SMALL = """2"""

PAPERSIZE_TABLOID = """3"""

PAPERSIZE_LEDGER = """4"""

PAPERSIZE_LEGAL = """5"""

PAPERSIZE_STATEMENT = """6"""

PAPERSIZE_EXECUTIVE = """7"""

PAPERSIZE_A3 = """8"""

PAPERSIZE_A4 = """9"""

PAPERSIZE_A4_SMALL = """10"""

PAPERSIZE_A5 = """11"""

ORIENTATION_PORTRAIT = """portrait"""

ORIENTATION_LANDSCAPE = """landscape"""

TABLESTYLES = tuple(['TableStyleMedium{0}'.format(i) for i in range(1, 29)] + [
    'TableStyleLight{0}'.format(i) for i in range(1, 22)] + [
    'TableStyleDark{0}'.format(i) for i in range(1, 12)])

PIVOTSTYLES = tuple(['PivotStyleMedium{0}'.format(i) for i in range(1, 29)] + [
    'PivotStyleLight{0}'.format(i) for i in range(1, 29)] + [
    'PivotStyleDark{0}'.format(i) for i in range(1, 29)])

FONT_PATTERN = """&"(?P<font>.+)\""""

COLOR_PATTERN = """&K(?P<color>[A-F0-9]{6})"""

SIZE_REGEX = """&(?P<size>\\d+\\s?)"""

FORMAT_REGEX = re.compile('{0}|{1}|{2}'.format(FONT_PATTERN, COLOR_PATTERN, SIZE_REGEX))

ITEM_REGEX = re.compile(
    """
    (&L(?P<left>.+?))?
    (&C(?P<center>.+?))?
    (&R(?P<right>.+?))?
    $"""
    , re.VERBOSE | re.DOTALL)

TRANSFORM = {'&[Tab]': '&A', '&[Pages]': '&N', '&[Date]': '&D', '&[Path]': '&Z',
    '&[Page]': '&P', '&[Time]': '&T', '&[File]': '&F', '&[Picture]': '&G'}

SUBS_REGEX = re.compile('|'.join(['({0})'.format(re.escape(k)) for k in TRANSFORM]))

FORMULAE = frozenset(FORMULAE)

CHAR_REGEX = re.compile('[\\001-\\031]')

ESCAPED_REGEX = re.compile('_x([0-9A-Fa-f]{4})_')

DEFAULT_ROW_HEIGHT = (15.0)

BASE_COL_WIDTH = (8)

DEFAULT_COLUMN_WIDTH = (BASE_COL_WIDTH + 5)

DEFAULT_LEFT_MARGIN = (0.7)

DEFAULT_TOP_MARGIN = (0.7874)

DEFAULT_HEADER = (0.3)

COORD_RE = re.compile('^[$]?([A-Za-z]{1,3})[$]?(\\d+)$')

RANGE_EXPR = """
[$]?(?P<min_col>[A-Za-z]{1,3})?
[$]?(?P<min_row>\\d+)?
(:[$]?(?P<max_col>[A-Za-z]{1,3})?
[$]?(?P<max_row>\\d+)?)?
"""

ABSOLUTE_RE = re.compile('^' + RANGE_EXPR + '$', re.VERBOSE)

SHEET_TITLE = """
(('(?P<quoted>([^']|'')*)')|(?P<notquoted>[^'^ ^!]*))!"""

SHEETRANGE_RE = re.compile('{0}(?P<cells>{1})(?=,?)'.format(SHEET_TITLE, RANGE_EXPR), re.
    VERBOSE)

PERCENT_REGEX = re.compile('^(?P<number>\\-?[0-9]*\\.?[0-9]*\\s?)\\%$')

TIME_REGEX = re.compile(
    """
^(?: # HH:MM and HH:MM:SS
(?P<hour>[0-1]{0,1}[0-9]{2}):
(?P<minute>[0-5][0-9]):?
(?P<second>[0-5][0-9])?$)
|
^(?: # MM:SS.
([0-5][0-9]):
([0-5][0-9])?\\.
(?P<microsecond>\\d{1,6}))
"""
    , re.VERBOSE)

NUMBER_REGEX = re.compile(
    '^-?([\\d]|[\\d]+\\.[\\d]*|\\.[\\d]+|[1-9][\\d]+\\.?[\\d]*)((E|e)[-+]?[\\d]+)?$'
    )

MAC_EPOCH = datetime.datetime(1904, 1, 1)

WINDOWS_EPOCH = datetime.datetime(1899, 12, 30)

CALENDAR_WINDOWS_1900 = WINDOWS_EPOCH

CALENDAR_MAC_1904 = MAC_EPOCH

SECS_PER_DAY = (86400)

ISO_FORMAT = """%Y-%m-%dT%H:%M:%SZ"""

ISO_REGEX = re.compile(
    """
(?P<date>(?P<year>\\d{4})-(?P<month>\\d{2})-(?P<day>\\d{2}))?T?
(?P<time>(?P<hour>\\d{2}):(?P<minute>\\d{2})(:(?P<second>\\d{2})(?P<microsecond>\\.\\d{1,3})?)?)?Z?"""
    , re.VERBOSE)

ISO_DURATION = re.compile(
    'PT((?P<hours>\\d+)H)?((?P<minutes>\\d+)M)?((?P<seconds>\\d+(\\.\\d{1,3})?)S)?'
    )

NS_REGEX = re.compile('({(?P<namespace>.*)})?(?P<localname>.*)')

MIN_ROW = (0)

MIN_COLUMN = (0)

MAX_COLUMN = (16384)

MAX_ROW = (1048576)

PACKAGE_PROPS = """docProps"""

PACKAGE_XL = """xl"""

PACKAGE_RELS = """_rels"""

PACKAGE_THEME = (PACKAGE_XL + '/' + 'theme')

PACKAGE_WORKSHEETS = (PACKAGE_XL + '/' + 'worksheets')

PACKAGE_CHARTSHEETS = (PACKAGE_XL + '/' + 'chartsheets')

PACKAGE_DRAWINGS = (PACKAGE_XL + '/' + 'drawings')

PACKAGE_CHARTS = (PACKAGE_XL + '/' + 'charts')

PACKAGE_IMAGES = (PACKAGE_XL + '/' + 'media')

PACKAGE_WORKSHEET_RELS = (PACKAGE_WORKSHEETS + '/' + '_rels')

PACKAGE_CHARTSHEETS_RELS = (PACKAGE_CHARTSHEETS + '/' + '_rels')

PACKAGE_PIVOT_TABLE = (PACKAGE_XL + '/' + 'pivotTables')

PACKAGE_PIVOT_CACHE = (PACKAGE_XL + '/' + 'pivotCache')

ARC_CONTENT_TYPES = """[Content_Types].xml"""

ARC_ROOT_RELS = (PACKAGE_RELS + '/.rels')

ARC_WORKBOOK_RELS = (PACKAGE_XL + '/' + PACKAGE_RELS + '/workbook.xml.rels')

ARC_CORE = (PACKAGE_PROPS + '/core.xml')

ARC_APP = (PACKAGE_PROPS + '/app.xml')

ARC_CUSTOM = (PACKAGE_PROPS + '/custom.xml')

ARC_WORKBOOK = (PACKAGE_XL + '/workbook.xml')

ARC_STYLE = (PACKAGE_XL + '/styles.xml')

ARC_THEME = (PACKAGE_THEME + '/theme1.xml')

ARC_SHARED_STRINGS = (PACKAGE_XL + '/sharedStrings.xml')

ARC_CUSTOM_UI = """customUI/customUI.xml"""

XML_NS = """http://www.w3.org/XML/1998/namespace"""

DCORE_NS = """http://purl.org/dc/elements/1.1/"""

DCTERMS_NS = """http://purl.org/dc/terms/"""

DCTERMS_PREFIX = """dcterms"""

DOC_NS = """http://schemas.openxmlformats.org/officeDocument/2006/"""

REL_NS = (DOC_NS + 'relationships')

COMMENTS_NS = (REL_NS + '/comments')

IMAGE_NS = (REL_NS + '/image')

VML_NS = (REL_NS + '/vmlDrawing')

VTYPES_NS = (DOC_NS + 'docPropsVTypes')

XPROPS_NS = (DOC_NS + 'extended-properties')

CUSTPROPS_NS = (DOC_NS + 'custom-properties')

EXTERNAL_LINK_NS = (REL_NS + '/externalLink')

CPROPS_FMTID = """{D5CDD505-2E9C-101B-9397-08002B2CF9AE}"""

PKG_NS = """http://schemas.openxmlformats.org/package/2006/"""

PKG_REL_NS = (PKG_NS + 'relationships')

COREPROPS_NS = (PKG_NS + 'metadata/core-properties')

CONTYPES_NS = (PKG_NS + 'content-types')

XSI_NS = """http://www.w3.org/2001/XMLSchema-instance"""

SHEET_MAIN_NS = """http://schemas.openxmlformats.org/spreadsheetml/2006/main"""

CHART_NS = """http://schemas.openxmlformats.org/drawingml/2006/chart"""

DRAWING_NS = """http://schemas.openxmlformats.org/drawingml/2006/main"""

SHEET_DRAWING_NS = """http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing"""

CHART_DRAWING_NS = """http://schemas.openxmlformats.org/drawingml/2006/chartDrawing"""

CUSTOMUI_NS = """http://schemas.microsoft.com/office/2006/relationships/ui/extensibility"""

NAMESPACES = {'cp': COREPROPS_NS, 'dc': DCORE_NS, DCTERMS_PREFIX: DCTERMS_NS, 'dcmitype':
    'http://purl.org/dc/dcmitype/', 'xsi': XSI_NS, 'vt': VTYPES_NS, 'xml':
    XML_NS, 'main': SHEET_MAIN_NS, 'cust': CUSTPROPS_NS}

WORKBOOK_MACRO = """application/vnd.ms-excel.%s.macroEnabled.main+xml"""

WORKBOOK = """application/vnd.openxmlformats-officedocument.spreadsheetml.%s.main+xml"""

SPREADSHEET = """application/vnd.openxmlformats-officedocument.spreadsheetml.%s+xml"""

SHARED_STRINGS = (SPREADSHEET % 'sharedStrings')

EXTERNAL_LINK = (SPREADSHEET % 'externalLink')

WORKSHEET_TYPE = (SPREADSHEET % 'worksheet')

COMMENTS_TYPE = (SPREADSHEET % 'comments')

STYLES_TYPE = (SPREADSHEET % 'styles')

CHARTSHEET_TYPE = (SPREADSHEET % 'chartsheet')

DRAWING_TYPE = """application/vnd.openxmlformats-officedocument.drawing+xml"""

CHART_TYPE = """application/vnd.openxmlformats-officedocument.drawingml.chart+xml"""

CHARTSHAPE_TYPE = """application/vnd.openxmlformats-officedocument.drawingml.chartshapes+xml"""

THEME_TYPE = """application/vnd.openxmlformats-officedocument.theme+xml"""

CPROPS_TYPE = """application/vnd.openxmlformats-officedocument.custom-properties+xml"""

XLTM = (WORKBOOK_MACRO % 'template')

XLSM = (WORKBOOK_MACRO % 'sheet')

XLTX = (WORKBOOK % 'template')

XLSX = (WORKBOOK % 'sheet')

EXT_TYPES = {'{78C0D931-6437-407D-A8EE-F0AAD7539E65}': 'Conditional Formatting',
    '{CCE6A557-97BC-4B89-ADB6-D9C93CAAB3DF}': 'Data Validation',
    '{05C60535-1F16-4FD2-B633-F4F36F0B64E0}': 'Sparkline Group',
    '{A8765BA9-456A-4DAB-B4F3-ACF838C121DE}': 'Slicer List',
    '{FC87AEE6-9EDD-4A0A-B7FB-166176984837}': 'Protected Range',
    '{01252117-D84E-4E92-8308-4BE1C098FCBB}': 'Ignored Error',
    '{F7C9EE02-42E1-4005-9D12-6889AFFD525C}': 'Web Extension',
    '{3A4CF648-6AED-40f4-86FF-DC5316D8AED3}': 'Slicer List',
    '{7E03D99C-DC04-49d9-9315-930204A7B6E9}': 'Timeline Ref'}

CTRL = """application/vnd.ms-excel.controlproperties+xml"""

ACTIVEX = """application/vnd.ms-office.activeX+xml"""

VBA = """application/vnd.ms-office.vbaProject"""

LXML = (lxml_available() and lxml_env_set())

DEFUSEDXML = (defusedxml_available() and defusedxml_env_set())

EMPTY_CELL = EmptyCell()

TIME_TYPES = (datetime.datetime, datetime.date, datetime.time, datetime.timedelta)

TIME_FORMATS = {datetime.datetime: numbers.FORMAT_DATE_DATETIME, datetime.date: numbers.
    FORMAT_DATE_YYYYMMDD2, datetime.time: numbers.FORMAT_DATE_TIME6,
    datetime.timedelta: numbers.FORMAT_DATE_TIMEDELTA}

STRING_TYPES = (str, bytes, CellRichText)

KNOWN_TYPES = (NUMERIC_TYPES + TIME_TYPES + STRING_TYPES + (bool, type(None)))

ILLEGAL_CHARACTERS_RE = re.compile('[\\000-\\010]|[\\013-\\014]|[\\016-\\037]')

ERROR_CODES = ('#NULL!', '#DIV/0!', '#VALUE!', '#REF!', '#NAME?', '#NUM!', '#N/A',
    '#GETTING_DATA')

TYPE_STRING = """s"""

TYPE_FORMULA = """f"""

TYPE_NUMERIC = """n"""

TYPE_BOOL = """b"""

TYPE_NULL = """n"""

TYPE_INLINE = """inlineStr"""

TYPE_ERROR = """e"""

TYPE_FORMULA_CACHE_STRING = """str"""

VALID_TYPES = (TYPE_STRING, TYPE_FORMULA, TYPE_NUMERIC, TYPE_BOOL, TYPE_NULL, TYPE_INLINE,
    TYPE_ERROR, TYPE_FORMULA_CACHE_STRING)

_TYPES = {int: 'n', float: 'n', str: 's', bool: 'b'}

BORDER_NONE = None

BORDER_DASHDOT = """dashDot"""

BORDER_DASHDOTDOT = """dashDotDot"""

BORDER_DASHED = """dashed"""

BORDER_DOTTED = """dotted"""

BORDER_DOUBLE = """double"""

BORDER_HAIR = """hair"""

BORDER_MEDIUM = """medium"""

BORDER_MEDIUMDASHDOT = """mediumDashDot"""

BORDER_MEDIUMDASHDOTDOT = """mediumDashDotDot"""

BORDER_MEDIUMDASHED = """mediumDashed"""

BORDER_SLANTDASHDOT = """slantDashDot"""

BORDER_THICK = """thick"""

BORDER_THIN = """thin"""

DEFAULT_BORDER = Border(left=Side(), right=Side(), top=Side(), bottom=Side(), diagonal=Side())

BUILTIN_FORMATS = {(0): 'General', (1): '0', (2): '0.00', (3): '#,##0', (4): '#,##0.00', (5):
    '"$"#,##0_);("$"#,##0)', (6): '"$"#,##0_);[Red]("$"#,##0)', (7):
    '"$"#,##0.00_);("$"#,##0.00)', (8): '"$"#,##0.00_);[Red]("$"#,##0.00)',
    (9): '0%', (10): '0.00%', (11): '0.00E+00', (12): '# ?/?', (13):
    '# ??/??', (14): 'mm-dd-yy', (15): 'd-mmm-yy', (16): 'd-mmm', (17):
    'mmm-yy', (18): 'h:mm AM/PM', (19): 'h:mm:ss AM/PM', (20): 'h:mm', (21):
    'h:mm:ss', (22): 'm/d/yy h:mm', (37): '#,##0_);(#,##0)', (38):
    '#,##0_);[Red](#,##0)', (39): '#,##0.00_);(#,##0.00)', (40):
    '#,##0.00_);[Red](#,##0.00)', (41):
    '_(* #,##0_);_(* \\(#,##0\\);_(* "-"_);_(@_)', (42):
    '_("$"* #,##0_);_("$"* \\(#,##0\\);_("$"* "-"_);_(@_)', (43):
    '_(* #,##0.00_);_(* \\(#,##0.00\\);_(* "-"??_);_(@_)', (44):
    '_("$"* #,##0.00_)_("$"* \\(#,##0.00\\)_("$"* "-"??_)_(@_)', (45):
    'mm:ss', (46): '[h]:mm:ss', (47): 'mmss.0', (48): '##0.0E+0', (49): '@'}

BUILTIN_FORMATS_MAX_SIZE = (164)

BUILTIN_FORMATS_REVERSE = dict([(value, key) for key, value in BUILTIN_FORMATS.items()])

FORMAT_GENERAL = BUILTIN_FORMATS[0]

FORMAT_TEXT = BUILTIN_FORMATS[49]

FORMAT_NUMBER = BUILTIN_FORMATS[1]

FORMAT_NUMBER_00 = BUILTIN_FORMATS[2]

FORMAT_NUMBER_COMMA_SEPARATED1 = BUILTIN_FORMATS[4]

FORMAT_NUMBER_COMMA_SEPARATED2 = """#,##0.00_-"""

FORMAT_PERCENTAGE = BUILTIN_FORMATS[9]

FORMAT_PERCENTAGE_00 = BUILTIN_FORMATS[10]

FORMAT_DATE_YYYYMMDD2 = """yyyy-mm-dd"""

FORMAT_DATE_YYMMDD = """yy-mm-dd"""

FORMAT_DATE_DDMMYY = """dd/mm/yy"""

FORMAT_DATE_DMYSLASH = """d/m/y"""

FORMAT_DATE_DMYMINUS = """d-m-y"""

FORMAT_DATE_DMMINUS = """d-m"""

FORMAT_DATE_MYMINUS = """m-y"""

FORMAT_DATE_XLSX14 = BUILTIN_FORMATS[14]

FORMAT_DATE_XLSX15 = BUILTIN_FORMATS[15]

FORMAT_DATE_XLSX16 = BUILTIN_FORMATS[16]

FORMAT_DATE_XLSX17 = BUILTIN_FORMATS[17]

FORMAT_DATE_XLSX22 = BUILTIN_FORMATS[22]

FORMAT_DATE_DATETIME = """yyyy-mm-dd h:mm:ss"""

FORMAT_DATE_TIME1 = BUILTIN_FORMATS[18]

FORMAT_DATE_TIME2 = BUILTIN_FORMATS[19]

FORMAT_DATE_TIME3 = BUILTIN_FORMATS[20]

FORMAT_DATE_TIME4 = BUILTIN_FORMATS[21]

FORMAT_DATE_TIME5 = BUILTIN_FORMATS[45]

FORMAT_DATE_TIME6 = BUILTIN_FORMATS[21]

FORMAT_DATE_TIME7 = """i:s.S"""

FORMAT_DATE_TIME8 = """h:mm:ss@"""

FORMAT_DATE_TIMEDELTA = """[hh]:mm:ss"""

FORMAT_DATE_YYMMDDSLASH = """yy/mm/dd@"""

FORMAT_CURRENCY_USD_SIMPLE = """"$"#,##0.00_-"""

FORMAT_CURRENCY_USD = """$#,##0_-"""

FORMAT_CURRENCY_EUR_SIMPLE = """[$EUR ]#,##0.00_-"""

COLORS = """\\[(BLACK|BLUE|CYAN|GREEN|MAGENTA|RED|WHITE|YELLOW)\\]"""

LITERAL_GROUP = """".*?\""""

LOCALE_GROUP = """\\[(?!hh?\\]|mm?\\]|ss?\\])[^\\]]*\\]"""

STRIP_RE = re.compile(f'{LITERAL_GROUP}|{LOCALE_GROUP}')

TIMEDELTA_RE = re.compile(
    '\\[hh?\\](:mm(:ss(\\.0*)?)?)?|\\[mm?\\](:ss(\\.0*)?)?|\\[ss?\\](\\.0*)?',
    re.I)

FILL_NONE = """none"""

FILL_SOLID = """solid"""

FILL_PATTERN_DARKDOWN = """darkDown"""

FILL_PATTERN_DARKGRAY = """darkGray"""

FILL_PATTERN_DARKGRID = """darkGrid"""

FILL_PATTERN_DARKHORIZONTAL = """darkHorizontal"""

FILL_PATTERN_DARKTRELLIS = """darkTrellis"""

FILL_PATTERN_DARKUP = """darkUp"""

FILL_PATTERN_DARKVERTICAL = """darkVertical"""

FILL_PATTERN_GRAY0625 = """gray0625"""

FILL_PATTERN_GRAY125 = """gray125"""

FILL_PATTERN_LIGHTDOWN = """lightDown"""

FILL_PATTERN_LIGHTGRAY = """lightGray"""

FILL_PATTERN_LIGHTGRID = """lightGrid"""

FILL_PATTERN_LIGHTHORIZONTAL = """lightHorizontal"""

FILL_PATTERN_LIGHTTRELLIS = """lightTrellis"""

FILL_PATTERN_LIGHTUP = """lightUp"""

FILL_PATTERN_LIGHTVERTICAL = """lightVertical"""

FILL_PATTERN_MEDIUMGRAY = """mediumGray"""

DEFAULT_EMPTY_FILL = PatternFill()

DEFAULT_GRAY_FILL = PatternFill(patternType='gray125')

UNDERLINE_DOUBLE = """double"""

UNDERLINE_DOUBLE_ACCOUNTING = """doubleAccounting"""

UNDERLINE_SINGLE = """single"""

UNDERLINE_SINGLE_ACCOUNTING = """singleAccounting"""

DEFAULT_FONT = Font(name='Calibri', sz=11, family=2, b=False, i=False, color=Color(theme=1
    ), scheme='minor')

COLOR_INDEX = ('00000000', '00FFFFFF', '00FF0000', '0000FF00', '000000FF', '00FFFF00',
    '00FF00FF', '0000FFFF', '00000000', '00FFFFFF', '00FF0000', '0000FF00',
    '000000FF', '00FFFF00', '00FF00FF', '0000FFFF', '00800000', '00008000',
    '00000080', '00808000', '00800080', '00008080', '00C0C0C0', '00808080',
    '009999FF', '00993366', '00FFFFCC', '00CCFFFF', '00660066', '00FF8080',
    '000066CC', '00CCCCFF', '00000080', '00FF00FF', '00FFFF00', '0000FFFF',
    '00800080', '00800000', '00008080', '000000FF', '0000CCFF', '00CCFFFF',
    '00CCFFCC', '00FFFF99', '0099CCFF', '00FF99CC', '00CC99FF', '00FFCC99',
    '003366FF', '0033CCCC', '0099CC00', '00FFCC00', '00FF9900', '00FF6600',
    '00666699', '00969696', '00003366', '00339966', '00003300', '00333300',
    '00993300', '00993366', '00333399', '00333333')

ARC_VBA = re.compile('|'.join(('xl/vba', 'xl/drawings/.*vmlDrawing\\d\\.vml',
    'xl/ctrlProps', 'customUI', 'xl/activeX', 'xl/media/.*\\.emf')))

KEYWORDS = frozenset(kwlist)

CELL_REF_RE = re.compile('(\\$?[A-Za-z]{1,3})(\\$?[1-9][0-9]{0,6})$')

SN_RE = re.compile('^[1-9](\\.[0-9]+)?[Ee]$')

WSPACE_RE = re.compile('[ \\n]+')

STRING_REGEXES = {'"': re.compile('"(?:[^"]*"")*[^"]*"(?!")'), "'": re.compile(
    "'(?:[^']*'')*[^']*'(?!')")}

TOKEN_ENDERS = """,;}) +-*/^&=><%"""

LITERAL = """LITERAL"""

OPERAND = """OPERAND"""

FUNC = """FUNC"""

PAREN = """PAREN"""

SEP = """SEP"""

OP_PRE = """OPERATOR-PREFIX"""

OP_IN = """OPERATOR-INFIX"""

OP_POST = """OPERATOR-POSTFIX"""

WSPACE = """WHITE-SPACE"""

TEXT = """TEXT"""

NUMBER = """NUMBER"""

LOGICAL = """LOGICAL"""

RANGE = """RANGE"""

CLOSE = """CLOSE"""

ARG = """ARG"""

ROW = """ROW"""

INTEGER_TYPES = (int,)

RESERVED = frozenset(['Print_Area', 'Print_Titles', 'Criteria', '_FilterDatabase',
    'Extract', 'Consolidate_Area', 'Sheet_Title'])

RESERVED_REGEX = re.compile('^_xlnm\\.(?P<name>{0})'.format(_names))

INVALID_TITLE_REGEX = re.compile('[\\\\*?:/\\[\\]]')

DEFAULT_CONFIG_PATH = """config.yaml"""

SUPPORTED_PDF_VERSIONS = ['1.4', '1.5', '1.6', '1.7', '2.0']

SUPPORTED_LANGUAGES = ['eng', 'fra', 'deu', 'spa', 'ita']

AA = """AA"""

AAA = """AAA"""

MISSING_ALT_TEXT = """Missing alternative text"""

INCORRECT_HEADING_ORDER = """Incorrect heading order"""

LOW_COLOR_CONTRAST = """Insufficient color contrast"""

MISSING_LANGUAGE = """Missing language specification"""

MISSING_TITLE = """Missing document title"""

COMPLEX_TABLE = """Complex table without proper headers"""

UNTAGGED_CONTENT = """Untagged content"""

DEFAULT_BATCH_SIZE = (10)

DEFAULT_MAX_WORKERS = (4)

DEFAULT_LANGUAGE = """eng"""

DEFAULT_PSM = (3)

DEFAULT_OEM = (3)

DEFAULT_MAX_ATTEMPTS = (3)

DEFAULT_BASE_DELAY = (1.0)

DEFAULT_MAX_DELAY = (60.0)

DEFAULT_EXPONENTIAL_BASE = (2.0)

DEFAULT_API_TIMEOUT = (30)

DEFAULT_OCR_TIMEOUT = (300)

