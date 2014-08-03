import os.path
import re
from wx import stc

from sci_lexer_map import sci_lexer_map

class Syntax(object):
    def __init__(self, name, description, lexer, file_patterns, comment_token="",
                 keywords="", indent_width=4, tab_width=8, use_tabs=False):
        self.name = name
        self.description = description
        self.lexer = lexer
        self.file_patterns = file_patterns
        self.comment_token = comment_token
        self.indent_width = indent_width
        self.tab_width = tab_width
        self.use_tabs = use_tabs
        self.keywords = keywords

    def get_style_specs(self, theme):
        if self.lexer in sci_lexer_map:
            lexer_constants = sci_lexer_map[self.lexer]
            for token_type_name, style_spec in theme:
                if token_type_name in lexer_constants:
                    yield (lexer_constants[token_type_name], style_spec)

keywords_c = """\
auto break case char const continue default do double else enum extern float
for goto if inline int long register restrict return short signed sizeof
static struct switch typedef union unsigned void volatile while _Alignas
_Alignof _Atomic _Bool _Complex _Generic _Imaginary _Noreturn _Static_assert
_Thread_local"""

keywords_cpp = """\
alignas alignof and and_eq asm auto bitand bitor bool break case catch char
char16_t char32_t class compl const constexpr const_cast continue decltype
default delete do double dynamic_cast else enum explicit export extern false
float for friend goto if inline int long mutable namespace new noexcept not
not_eq nullptr operator or or_eq private protected public register
reinterpret_cast return short signed sizeof static static_assert static_cast
struct switch template this thread_local throw true try typedef typeid typename
union unsigned using virtual void volatile wchar_t while xor xor_eq"""

keywords_java = """\
abstract continue for new switch assert default goto package synchronized
boolean do if private this break double implements protected throw byte else
import public throws case enum instanceof return transient catch extends int
short try char final interface static void class finally long strictfp volatile
const float native super while"""

keywords_csharp = """\
abstract as base bool break byte case catch char checked class const continue
decimal default delegate do double else enum event explicit extern false finally
fixed float for foreach goto if implicit in int interface internal is lock long
namespace new null object operator out override params private protected public
readonly ref return sbyte sealed short sizeof stackalloc static string struct
switch this throw true try typeof uint ulong unchecked unsafe ushort using
virtual void volatile while
add alias ascending async await descending dynamic from get global group into
join let orderby partial remove select set value var where yield"""

keywords_javascript = """\
break case catch class const continue debugger default delete do else enum
export extends finally for function if implements import in instanceof interface
let new package private protected return static super switch this throw try
typeof var void while with yield
"""

keywords_python = """\
and as assert break class continue def del elif else except exec finally for
from global if import in is lambda not or pass print raise return try
while with yield None True False"""

keywords_perl = """\
NULL __FILE__ __LINE__ __PACKAGE__ __DATA__ __END__ AUTOLOAD
BEGIN CORE DESTROY END EQ GE GT INIT LE LT NE CHECK abs accept
alarm and atan2 bind binmode bless caller chdir chmod chomp chop
chown chr chroot close closedir cmp connect continue cos crypt
dbmclose dbmopen defined delete die do dump each else elsif endgrent
endhostent endnetent endprotoent endpwent endservent eof eq eval
exec exists exit exp fcntl fileno flock for foreach fork format
formline ge getc getgrent getgrgid getgrnam gethostbyaddr gethostbyname
gethostent getlogin getnetbyaddr getnetbyname getnetent getpeername
getpgrp getppid getpriority getprotobyname getprotobynumber getprotoent
getpwent getpwnam getpwuid getservbyname getservbyport getservent
getsockname getsockopt glob gmtime goto grep gt hex if index
int ioctl join keys kill last lc lcfirst le length link listen
local localtime lock log lstat lt map mkdir msgctl msgget msgrcv
msgsnd my ne next no not oct open opendir or ord our pack package
pipe pop pos print printf prototype push quotemeta qu
rand read readdir readline readlink readpipe recv redo
ref rename require reset return reverse rewinddir rindex rmdir
scalar seek seekdir select semctl semget semop send setgrent
sethostent setnetent setpgrp setpriority setprotoent setpwent
setservent setsockopt shift shmctl shmget shmread shmwrite shutdown
sin sleep socket socketpair sort splice split sprintf sqrt srand
stat study sub substr symlink syscall sysopen sysread sysseek
system syswrite tell telldir tie tied time times truncate
uc ucfirst umask undef unless unlink unpack unshift untie until
use utime values vec wait waitpid wantarray warn while write
xor given when default break say state UNITCHECK __SUB__ fc"""

keywords_awk = """\
BEGIN END
if else while do for in break continue delete exit function return
print printf sprintf
system close getline next nextfile fflush
atan2 cos exp int log rand sin sqrt srand
asort asorti gensub sub gsub index length match split
strtonum substr tolower toupper
mktime strftime systime
and compl lshift or rshift xor
bindtextdomain dcgettext dcngettext
ARGC ARGIND ARGV BINMODE CONVFMT ENVIRON ERRNO FIELDWIDTHS
FILENAME FNR FS IGNORECASE LINT NF NR OFMT OFS ORS PROCINFO
RS RT RSTART RLENGTH SUBSEP TEXTDOMAIN"""

keywords_bash = """\
alias ar asa awk banner basename bash bc bdiff break
bunzip2 bzip2 cal calendar case cat cc cd chmod cksum
clear cmp col comm compress continue cp cpio crypt
csplit ctags cut date dc dd declare deroff dev df diff diff3
dircmp dirname do done du echo ed egrep elif else env
esac eval ex exec exit expand export expr false fc
fgrep fi file find fmt fold for function functions
getconf getopt getopts grep gres hash head help
history iconv id if in integer jobs join kill local lc
let line ln logname look ls m4 mail mailx make
man mkdir more mt mv newgrp nl nm nohup ntps od
pack paste patch pathchk pax pcat perl pg pr print
printf ps pwd read readonly red return rev rm rmdir
sed select set sh shift size sleep sort spell
split start stop strings strip stty sum suspend
sync tail tar tee test then time times touch tr
trap true tsort tty type typeset ulimit umask unalias
uname uncompress unexpand uniq unpack unset until
uudecode uuencode vi vim vpax wait wc whence which
while who wpaste wstart xargs zcat
chgrp chown chroot dir dircolors
factor groups hostid install link md5sum mkfifo
mknod nice pinky printenv ptx readlink seq
sha1sum shred stat su tac unlink users vdir whoami yes"""

keywords_sql = """\
absolute action add admin after aggregate alias all allocate alter and any are
array as asc assertion at authorization before begin binary bit blob body
boolean both breadth by call cascade cascaded case cast catalog char character
check class clob close collate collation column commit completion connect
connection constraint constraints constructor continue corresponding create
cross cube current current_date current_path current_role current_time
current_timestamp current_user cursor cycle data date day deallocate dec decimal
declare default deferrable deferred delete depth deref desc describe descriptor
destroy destructor deterministic dictionary diagnostics disconnect distinct
domain double drop dynamic each else end end-exec equals escape every except
exception exec execute exists exit external false fetch first float for foreign
found from free full function general get global go goto grant group grouping
having host hour identity if ignore immediate in indicator initialize initially
inner inout input insert int integer intersect interval into is isolation
iterate join key language large last lateral leading left less level like limit
locallocaltime localtimestamp locator map match merge minute modifies modify
module month names national natural nchar nclob new next no none not null
numeric object of off old on only open operation option or order ordinality out
outer output package pad parameter parameters partial path postfix precision
prefix preorder prepare preserve primary prior privileges procedure public read
reads real recursive ref references referencing relative restrict result return
returns revoke right role rollback rollup routine row rows savepoint schema
scroll scope search second section select sequence session session_user set sets
size smallint some| space specific specifictype sql sqlexception sqlstate
sqlwarning start state statement static structure system_user table temporary
terminate than then time timestamp timezone_hour timezone_minute to trailing
transaction translation treat trigger true under union unique unknown unnest
update usage user using value values varchar variable varying view when whenever
where with without work write year zone"""

keywords_plsql = """\
all alter and any array as asc at authid avg begin between binary_integer body
boolean bulk by char char_base check close cluster collect comment commit
compress connect constant create current currval cursor date day declare decimal
default delete desc distinct do drop else elsif end exception exclusive execute
exists exit extends false fetch float for forall from function goto group having
heap hour if immediate in index indicator insert integer interface intersect
interval into is isolation java level like limited lock long loop max min minus
minute mlslabel mod mode month natural naturaln new nextval nocopy not nowait
null number number_base ocirowid of on opaque open operator option or order
organization others out package partition pctfree pls_integer positive positiven
pragma prior private procedure public raise range raw real record ref release
return reverse rollback row rowid rownum rowtype savepoint second select
separate set share smallint space sql sqlcode sqlerrm start stddev subtype
successful sum synonym sysdate table then time timestamp to trigger true type
uid union unique update use user validate values varchar varchar2 variance view
when whenever where while with work write year zone"""

keywords_batch = """\
rem set if exist errorlevel for in do break call chcp cd chdir choice cls
country ctty date del erase dir echo exit goto loadfix loadhigh mkdir md move
path pause prompt rename ren rmdir rd shift time type ver verify vol com con lpt
nul color copy defined else not start append attrib chkdsk comp diskcomp"""

keywords_scheme = """\
quote lambda if set! include include-ci cond else case and or when unless
cond-expand library not let let* letrec letrec* let-values let-values* begin do
delay delay-force force promise? make-promise make-parameter parameterize guard
quasiquote unquote unquote-splicing case-lambda let-syntax letrec-syntax
syntax-rules syntax-error import only except prefix rename define define-values
define-syntax define-record-type define-library export
include-library-declarations
eqv? eq? equal? number? complex? real? rational? integer? exact? inexact?
exact-integer? finite? infinite? nan? zero? positive? negative? odd? even? max
min + * - / abs floor/ floor-quotient floor-remainder truncate/
truncate-quotient truncate-remainder quotient remainder modulo gcd lcm numerator
denominator floor ceiling truncate round rationalize exp log sin cos tan asin
acos atan square sqrt exact-integer-sqrt expt make-rectangular make-polar
real-part imag-part magnitude angle inexact exact number->string string->number
boolean? boolean=? pair? cons car cdr set-car! set-cdr! caar cadr cdar cddr
caaar caadr cadar caddr cdaar cdadr cddar cdddr caaaar caaadr caadar caaddr
cadaar cadadr caddar cadddr cdaaar cdaadr cdadar cdaddr cddaar cddadr cdddar
cddddr null? list? make-list list length append reverse list-tail list-ref
list-set! memq memv member assq assv assoc list-copy symbol? symbol->string
string->symbol char? char=? char<? char>? char<=? char>=? char-ci=? char-ci<?
char-ci>? char-ci<=? char-ci>=? char-alphabetic? char-numeric? char-whitespace?
char-upper-case? char-lower-case? digit-value char->integer integer->char
char-upcase char-downcase char-foldcase string? make-string string string-length
string-ref string-set! string=? string-ci=? string<? string-ci<? string>?
string-ci>? string<=? string-ci<=? string>=? string-ci>=? string-upcase
string-downcase string-foldcase substring string-append string->list
list->string string-copy string-copy! string-fill! vector? make-vector vector
vector-length vector-ref vector-set! vector->list list->vector vector->string
string->vector vector-copy vector-copy! vector-append vector-fill! bytevector?
make-bytevector bytevector bytevector-length bytevector-u8-ref
bytevector-u8-set! bytevector-copy bytevector-copy! bytevector-append
utf8->string string->utf8 procedure? apply map string-map vector-map for-each
string-for-each vector-for-each call-with-current-continuation call/cc values
call-with-values dynamic-wind with-exception-handler raise raise-continuable
error error-object? error-object-message error-object-irritants read-error?
file-error? environment scheme-report-environment null-environment
interactive-environment eval call-with-port call-with-input-file
call-with-output-file input-port? output-port? textual-port? binary-port? port?
input-port-open? output-port-open? current-input-port current-output-port
current-error-port with-input-from-file with-output-to-file open-input-file
open-binary-input-file open-output-file open-binary-output-file close-port
close-input-port close-output-port open-input-string open-output-string
get-output-string open-input-bytevector open-output-bytevector
get-input-bytevector read read-char peek-char read-line eof-object? eof-object
char-ready? read-string read-u8 peek-u8 u8-ready? read-bytevector
read-bytevector! write write-shared write-simple display newline write-char
write-string write-u8 write-bytevector flush-output-port load file-exists?
delete-file command-line exit emergency-exit get-environment-variable
get-environment-variables current-second current-jiffy jiffies-per-second
features"""

keywords_ruby = """\
BEGIN END __ENCODING__ __END__ __FILE__ __LINE__ alias and begin break case
class def defined? do else elsif end ensure false for if in module next nil
not or redo rescue retry return self super then true undef unless until when
while yield"""

keywords_lua = """
and break do else elseif end false for function if in local nil not or repeat
return then true until while
"""

keywords_pascal = """\
absolute and array asm begin case const constructor destructor div do downto
else end file for function goto if implementation in inherited inline interface
label mod nil not object of operator or packed procedure program record
reintroduce repeat self set shl shr string then to type unit until uses var
while with xor
dispose exit false new true
as class dispinterface except exports finalization finally initialization inline
is library on out packed property raise resourcestring threadvar try  absolute
abstract alias assembler bitpacked break cdecl continue cppdecl cvar default
deprecated dynamic enumerator experimental export external far far16 forward
generic helper implements index interrupt iochecks local message name near
nodefault noreturn nostackframe oldfpccall otherwise overload override pascal
platform private protected public published read register reintroduce result
safecall saveregisters softfloat specialize static stdcall stored strict
unaligned unimplemented varargs virtual write"""

keywords_modula2 = """\
and elsif loop repeat array end mod return begin exit module set by export not
then case for of to const from or type definition if pointer until div
implementation procedure var do import qualified while else in record with"""

keywords_freebasic = """\
append as asc asin asm atan2 atn beep bin binary bit bitreset bitset bload
bsave byref byte byval call callocate case cbyte cdbl cdecl chain chdir chr
cint circle clear clng clngint close cls color command common cons const
continue cos cshort csign csng csrlin cubyte cuint culngint cunsg curdir
cushort custom cvd cvi cvl cvlongint cvs cvshort data date deallocate declare
defbyte defdbl defined defint deflng deflngint defshort defsng defstr defubyte
defuint defulngint defushort dim dir do double draw dylibload dylibsymbol else
elseif end enum environ environ$ eof eqv erase err error exec exepath exit exp
export extern field fix flip for fre freefile function get getjoystick getkey
getmouse gosub goto hex hibyte hiword if iif imagecreate imagedestroy imp
inkey inp input instr int integer is kill lbound lcase left len let lib line
lobyte loc local locate lock lof log long longint loop loword lset ltrim
mid mkd mkdir mki mkl mklongint mks mkshort mod multikey mutexcreate
mutexdestroy mutexlock mutexunlock name next not oct on once open option or out
output overload paint palette pascal pcopy peek peeki peeks pipe pmap point
pointer poke pokei pokes pos preserve preset print private procptr pset ptr
public put random randomize read reallocate redim rem reset restore resume
resume next return rgb rgba right rmdir rnd rset rtrim run sadd screen
screencopy screeninfo screenlock screenptr screenres screenset screensync
screenunlock seek statement seek function selectcase setdate setenviron
setmouse settime sgn shared shell shl short shr sin single sizeof sleep space
spc sqr static stdcall step stop str string string strptr sub swap system tab
tan then threadcreate threadwait time time timer to trans trim type ubound
ubyte ucase uinteger ulongint union unlock unsigned until ushort using va_arg
va_first va_next val val64 valint varptr view viewprint wait wend while width
window windowtitle with write xor zstring"""

keywords_vb = """\
addhandler addressof alias and andalso ansi as assembly attribute auto base
begin binary boolean byref byte byval call case catch cbool cbyte cchar cdate
cdbl cdec char cint class clng cobj compare const continue csbyte cshort csng
cstr ctype cuint culng currency cushort custom date decimal declare default
defbool defbyte defcur defdate defdbl defdec defint deflng defobj defsng defstr
defvar delegate dim directcast do double each else elseif empty end endif enum
eqv erase error event exit explicit externalsource false finally for friend
function get gettype global gosub goto handles if imp implements imports in
inherits input integer interface is isfalse isnot istrue len let lib like load
lock long loop lset me mid midb mod module mustinherit mustoverride my mybase
myclass namespace narrowing new next not nothing notinheritable notoverridable
null object of off on operator option optional or orelse overloads overridable
overrides paramarray partial preserve print private property protected public
raiseevent randomize readonly redim region rem removehandler resume return rset
sbyte seek select set shadows shared short single static step stop strict string
structure sub synclock text then throw time to true try trycast type typeof
uinteger ulong unicode unload until ushort using variant wend when while
widening with withevents writeonly xor"""

keywords_blitzbasic = """\
abs accepttcpstream acos after and apptitle asc asin atan atan2
automidhandle autosuspend availvidmem backbuffer banksize before bin calldll
case ceil changedir channelpan channelpitch channelplaying channelvolume chr
closedir closefile closemovie closetcpserver closetcpstream closeudpstream cls
clscolor color colorblue colorgreen colorred commandline const copybank copyfile
copyimage copypixel copypixelfast copyrect copystream cos countgfxdrivers
countgfxmodes counthostips createbank createdir createimage createnetplayer
createprocess createtcpserver createtimer createudpstream currentdate currentdir
currenttime data debuglog default delay delete deletedir deletefile
deletenetplayer desktopbuffer dim dottedip drawblock drawblockrect drawimage
drawimagerect drawmovie each else else if elseif end end function end if end
select end type endgraphics endif eof execfile exit exp false field filepos
filesize filetype first flip float floor flushjoy flushkeys flushmouse
fontheight fontname fontsize fontstyle fontwidth for forever freebank freefont
freeimage freesound freetimer frontbuffer function gammablue gammagreen gammared
getcolor getenv getkey getmouse gfxdrivername gfxmodedepth gfxmodeexists
gfxmodeformat gfxmodeheight gfxmodewidth global gosub goto grabimage graphics
graphicsbuffer graphicsdepth graphicsformat graphicsheight graphicswidth
handleimage hex hidepointer hostip hostnetgame if imagebuffer imageheight
imagerectcollide imagerectoverlap imagescollide imagesoverlap imagewidth
imagexhandle imageyhandle include input insert instr int joinnetgame joydown
joyhat joyhit joypitch joyroll joytype joyu joyudir joyv joyvdir joyx joyxdir
joyy joyyaw joyydir joyz joyzdir keydown keyhit keywait last left len line
loadanimimage loadbuffer loadfont loadimage loadsound local lockbuffer
lockedformat lockedpitch lockedpixels log log10 loopsound lower lset maskimage
mid midhandle millisecs mod morefiles mousedown mousehit mousex mousexspeed
mousey mouseyspeed mousez mousezspeed movemouse movieheight movieplaying
moviewidth netmsgdata netmsgfrom netmsgto netmsgtype netplayerlocal
netplayername new next nextfile not null openfile openmovie opentcpstream or
origin oval pausechannel pausetimer peekbyte peekfloat peekint peekshort pi
playcdtrack playmusic playsound plot pokebyte pokefloat pokeint pokeshort print
queryobject rand read readavail readbyte readbytes readdir readfile readfloat
readint readline readpixel readpixelfast readshort readstring rect rectsoverlap
recvnetmsg recvudpmsg repeat replace resettimer resizebank resizeimage restore
resumechannel resumetimer return right rnd rndseed rotateimage rset runtimeerror
sar savebuffer saveimage scaleimage scanline seedrnd seekfile select sendnetmsg
sendudpmsg setbuffer setenv setfont setgamma setgfxdriver sgn shl showpointer
shr sin soundpan soundpitch soundvolume sqr startnetgame step stop stopchannel
stopnetgame str string stringheight stringwidth systemproperty tan tcpstreamip
tcpstreamport tcptimeouts text tformfilter tformimage then tileblock tileimage
timerticks to totalvidmem trim true type udpmsgip udpmsgport udpstreamip
udpstreamport udptimeouts unlockbuffer until updategamma upper viewport vwait
waitkey waitmouse waittimer wend while write writebyte writebytes writefile
writefloat writeint writeline writepixel writepixelfast writeshort writestring"""

keywords_fortran77 = """\
assign backspace block data call close common continue data dimension do else
else if end endfile endif entry equivalence external format function goto if
implicit inquire intrinsic open parameter pause print program read return rewind
rewrite save stop subroutine then write"""

keywords_fortran = keywords_fortran77 + """
abstract all allocatable allocate associate asynchronous bind block case class
codimension concurrent contains contiguous critical cycle deallocate deferred do
elemental elsewhere enum enumerator error exit extends final flush forall
generic images import include intent interface lock memory module namelist
non_overridable nopass nullify only operator optional pass pointer private
procedure protected public pure recursive result select sequence stop submodule
sync sync sync target unlock use value volatile wait where while"""

keywords_css = """\
above absolute ActiveBorder ActiveCaption always AppWorkspace aqua armenian
ascent auto avoid azimuth Background background background-attachment
background-color background-image background-position background-repeat baseline
baseline bbox behind below bidi-override black blink block blue bold bolder
border border-bottom border-bottom-color border-bottom-style border-bottom-width
border-collapse border-color border-color border-left border-left-color
border-left-style border-left-width border-right border-right-color
border-right-style border-right-width border-spacing border-style border-style
border-top border-top-color border-top-style border-top-width border-width both
bottom bottom ButtonFace ButtonHighlight ButtonShadow ButtonText cap-height
capitalize caption caption-side CaptionText center center-left center-right
centerline child circle cjk-ideographic clear clip close-quote code collapse
color compact condensed content continuous counter-increment counter-reset crop
cross crosshair cue cue-after cue-before cursor dashed decimal
decimal-leading-zero default definition-src descent digits direction disc
display dotted double e-resize elevation embed empty-cells expanded
extra-condensed extra-expanded far-left far-right fast faster female fixed fixed
float font font-family font-size font-size-adjust font-stretch font-style
font-variant font-weight fuchsia georgian gray GrayText green groove hebrew
height help hidden hide high higher Highlight HighlightText hiragana
hiragana-iroha icon InactiveBorder InactiveCaption InactiveCaptionText
InfoBackground InfoText inherit inline inline-table inset inside italic justify
katakana katakana-iroha landscape large larger left left left-side leftwards
letter-spacing level lighter lime line-height line-through list-item list-style
list-style-image list-style-position list-style-type loud low lower lower-alpha
lower-greek lower-latin lower-roman lowercase ltr male margin margin-bottom
margin-left margin-right margin-top marker marker-offset marks maroon mathline
max-height max-width medium medium medium medium Menu menu MenuText message-box
middle min-height min-width mix move n-resize narrower navy ne-resize
no-close-quote no-open-quote no-repeat no-wrap none normal nw-resize oblique
olive once open-quote orphans outline outline-color outline-style outline-width
outset outside overflow overline padding padding-bottom padding-left
padding-right padding-top page page-break-after page-break-before
page-break-inside panose-1 pause pause-after pause-before pitch pitch-range
play-during pointer portrait position pre purple quotes red relative repeat
repeat-x repeat-y richness ridge right right right-side rightwards rtl run-in
s-resize scroll scroll Scrollbar se-resize semi-condensed semi-expanded separate
show silent silver size slope slow slower small small-caps small-caption smaller
soft solid speak speak-header speak-numeral speak-punctuation speech-rate
spell-out square src static status-bar stemh stemv stress sub super sw-resize
table table-caption table-cell table-column table-column-group
table-footer-group table-header-group table-layout table-row table-row-group
teal text text-align text-bottom text-decoration text-indent text-shadow
text-top text-transform thick thin ThreeDDarkShadow ThreeDFace ThreeDHighlight
ThreeDLightShadow ThreeDShadow top top topline transparent ultra-condensed
ultra-expanded underline unicode-bidi unicode-range units-per-em upper-alpha
upper-latin upper-roman uppercase vertical-align visibility visible voice-family
volume w-resize wait white white-space wider widows width widths Window
WindowFrame WindowText word-spacing x-fast x-height x-high x-large x-loud x-low
x-slow x-small x-soft xx-large xx-small yellow z-index"""

keywords_eiffel = """\
alias all and any as bit boolean check class character clone create creation
current debug deferred div do double else elseif end ensure equal expanded
export external false feature forget from frozen general if implies indexing
infix inherit inspect integer invariant is language like local loop mod name
nochange none not obsolete old once or platform pointer prefix precursor real
redefine rename require rescue result retry select separate string strip then
true undefine unique until variant void when xor"""

keywords_haskell = """\
case ccall class data default deriving do dynamic else export forall foreign
hiding if import in infix infixl infixr instance label let module newtype of
prim safe stdcall then threadsafe type unsafe where"""

keywords_ocaml = """\
and as asr assert begin class constraint do done downto else end exception
external false for fun function functor if in include inherit initializer land
lazy let lor lsl lsr lxor match method mod module mutable new object of open or
private rec sig struct then to true try type val virtual when while with"""

keywords_sml = """\
abstype and andalso as case datatype div do else end eqtype exception false fn
fun functor handle if in include infix infixr let local mod nonfix not of op
open orelse raise rec sharing sig signature struct structure then true type use
val while with withtype"""

keywords_erlang = """\
after and andalso band begin bnot bor bsl bsr bxor case catch cond div end fun
if let not of or orelse query receive rem try when xor"""

keywords_tcl = """\
after append array auto_execok auto_import auto_load auto_load_index
auto_qualify beep bell bgerror binary bind bindtags bitmap break button canvas
case catch cd checkbutton clipboard clock close colors concat console continue
cursors dde default destroy echo else elseif encoding entry eof error eval event
exec exit expr fblocked fconfigure fcopy file fileevent flush focus font for
foreach format frame gets glob global grab grid history http if image incr info
Inter-client interp join keysyms label labelframe lappend lindex linsert list
listbox llength load loadTk lower lrange lreplace lsearch lset lsort memory menu
menubutton message msgcat namespace open option options pack package panedwindow
photo pid pkg::create pkg_mkIndex place Platform-specific proc puts pwd
radiobutton raise re_syntax read regexp registry regsub rename resource return
scale scan scrollbar seek selection send set socket source spinbox split string
subst switch tclLog tclMacPkgSearch tclPkgSetup tclPkgUnknown tell text time tk
tk_chooseColor tk_chooseDirectory tk_dialog tk_focusNext tk_getOpenFile
tk_messageBox tk_optionMenu tk_popup tk_setPalette tkerror tkvars tkwait
toplevel trace unknown unset update uplevel upvar variable vwait while winfo
wish wm"""

keywords_smalltalk = """\
ifTrue: ifFalse: whileTrue: whileFalse: ifNil: ifNotNil: whileTrue whileFalse
repeat isNil notNil"""

syntax_plain = Syntax("plain", "Plain Text", stc.STC_LEX_NULL, "*")

syntax_list = [
    Syntax("c", "C", stc.STC_LEX_CPP, "*.c;*.h", "//", keywords_c),
    Syntax("cpp", "C++", stc.STC_LEX_CPP, "*.cpp;*.cxx;*.cc;*.hpp;*.hxx;*.hh", "//", keywords_cpp),
    Syntax("objc", "Objective-C", stc.STC_LEX_CPP, "*.m", "//", keywords_c),
    Syntax("objcpp", "Objective-C++", stc.STC_LEX_CPP, "*.mm", "//", keywords_cpp),
    Syntax("java", "Java", stc.STC_LEX_CPP, "*.java", "//", keywords_java),
    Syntax("csharp", "C#", stc.STC_LEX_CPP, "*.cs", "//", keywords_csharp),
    Syntax("javascript", "JavaScript", stc.STC_LEX_CPP, "*.js;*.es", "//", keywords_javascript),
    Syntax("python", "Python", stc.STC_LEX_PYTHON, "*.py", "#", keywords_python),
    Syntax("html", "HTML", stc.STC_LEX_HTML, "*.html;*.htm"),
    Syntax("sgml", "SGML", stc.STC_LEX_HTML, "*.sgml"),
    Syntax("xml", "XML", stc.STC_LEX_XML, "*.xml;*.xhtml;*.xht;*.xslt;*.rdf;*.rss;*.atom;*.dbk;*.kml"),
    Syntax("css", "CSS", stc.STC_LEX_CSS, "*.css", "", keywords_css),
    Syntax("perl", "Perl", stc.STC_LEX_PERL, "*.pl;*.pm;*.pod", "#", keywords_perl),
    Syntax("awk", "Awk", stc.STC_LEX_PERL, "*.awk", "#", keywords_awk),
    Syntax("bash", "Bash", stc.STC_LEX_BASH, "*.sh", "#", keywords_bash),
    Syntax("sql", "SQL", stc.STC_LEX_SQL, "*.sql", "#", keywords_sql),
    Syntax("plsql", "PL/SQL", stc.STC_LEX_SQL, "*.spec;*.body;*.sps;*.spb;*.sf;*.sp", "#", keywords_plsql),
    Syntax("diff", "Diff", stc.STC_LEX_DIFF, "*.diff;*.patch"),
    Syntax("makefile", "Makefile", stc.STC_LEX_MAKEFILE, "Makefile*;makefile*;GNUmakefile*;*.mak;*.mk", "#",
           indent_width = 8, tab_width = 8, use_tabs = True),
    Syntax("batch", "Batch File", stc.STC_LEX_BATCH, "*.bat;*.cmd;*.nt", "REM ", keywords_batch),
    Syntax("scheme", "Scheme", stc.STC_LEX_LISP, "*.scm;*.ss", ";", keywords_scheme),
    Syntax("ruby", "Ruby", stc.STC_LEX_RUBY, "*.rb;*.rbw;*.rake;*.rjs;Rakefile", "#", keywords_ruby),
    Syntax("lua", "Lua", stc.STC_LEX_LUA, "*.lua", "#", keywords_lua),
    Syntax("pascal", "Pascal", stc.STC_LEX_PASCAL, "*.dpr;*.dpk;*.pas;*.dfm;*.inc;*.pp", "//", keywords_pascal),
    Syntax("modula2", "Modula-2", stc.STC_LEX_PASCAL, "*.mod;*.def", "", keywords_modula2),
    Syntax("freebasic", "FreeBasic", stc.STC_LEX_FREEBASIC, "*.bas;*.bi", "'", keywords_freebasic),
    Syntax("vb", "Visual Basic", stc.STC_LEX_VB, "*.vb;*.bas;*.frm;*.cls;*.ctl;*.pag;*.dsr;*.dob", "'", keywords_vb),
    Syntax("blitzbasic", "Blitz Basic", stc.STC_LEX_BLITZBASIC, "*.bb", "'", keywords_blitzbasic),
    Syntax("latex", "LaTeX", stc.STC_LEX_LATEX, "*.tex;*.sty", "%"),
    Syntax("fortran77", "FORTRAN 77", stc.STC_LEX_F77, "*.f;*.for", "*", keywords_fortran77),
    Syntax("fortran", "Fortran", stc.STC_LEX_FORTRAN, "*.f90;*.f95;*.f2k", "*", keywords_fortran),
    Syntax("eiffel", "Eiffel", stc.STC_LEX_EIFFEL, "*.e", "--", keywords_eiffel),
    Syntax("haskell", "Haskell", stc.STC_LEX_HASKELL, "*.hs", "--", keywords_haskell),
    Syntax("ocaml", "OCaml", stc.STC_LEX_CAML, "*.ml;*.mli", "", keywords_ocaml),
    Syntax("sml", "Standard ML", stc.STC_LEX_SML, "*.sml", "", keywords_sml),
    Syntax("erlang", "Erlang", stc.STC_LEX_ERLANG, "*.erl;*.hrl", "%", keywords_erlang),
    Syntax("tcl", "TCL", stc.STC_LEX_TCL, "*.tcl;*.exp", "#", keywords_tcl),
    Syntax("smalltalk", "Smalltalk", stc.STC_LEX_SMALLTALK, "*.st", '"', keywords_smalltalk),
    syntax_plain,
]

syntax_dict = dict((syntax.name, syntax) for syntax in syntax_list)

def filename_syntax_re():
    patterns = []
    for syntax in syntax_list:
        ptn = "|".join(re.escape(ext).replace("\\*", ".*") for ext in syntax.file_patterns.split(";"))
        ptn = "(?P<%s>^(%s)$)" % (syntax.name, ptn)
        patterns.append(ptn)
    return re.compile("%s" % "|".join(patterns))

filename_syntax_re = filename_syntax_re()

def syntax_from_filename(filename):
    return syntax_dict[filename_syntax_re.match(os.path.basename(filename)).lastgroup]
