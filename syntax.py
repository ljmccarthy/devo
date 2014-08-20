import os.path
import re
from wx import stc

from lexer_token_map import lexer_token_map
from util import compile_file_patterns

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
        file_patterns_list = file_patterns.split(";")
        file_patterns = ";".join(file_patterns_list + [ext + ".in" for ext in file_patterns_list])
        self.file_regex = compile_file_patterns(file_patterns)

    def get_style_specs(self, theme):
        if self.lexer in lexer_token_map:
            token_map = lexer_token_map[self.lexer]
            for token_type_name, style_spec in theme:
                for scilex_constant in token_map.get(token_type_name, []):
                    yield (scilex_constant, style_spec)

keywords_c = """\
_Alignas _Alignof _Atomic _Bool _Complex _Generic _Imaginary _Noreturn
_Static_assert _Thread_local auto break case char const continue default do
double else enum extern float for goto if inline int long register restrict
return short signed sizeof static struct switch typedef union unsigned void
volatile while"""

keywords_cpp = """\
alignas alignof and and_eq asm auto bitand bitor bool break case catch char
char16_t char32_t class compl const const_cast constexpr continue decltype
default delete do double dynamic_cast else enum explicit export extern false
float for friend goto if inline int long mutable namespace new noexcept not
not_eq nullptr operator or or_eq private protected public register
reinterpret_cast return short signed sizeof static static_assert static_cast
struct switch template this thread_local throw true try typedef typeid typename
union unsigned using virtual void volatile wchar_t while xor xor_eq"""

keywords_objc = """
@autoreleasepool @catch @class @compatibility_alias @defs @dynamic @encode @end
@finally @implementation @interface @optional @package @private @property
@protected @protocol @public @required @selector @synchronized @synthesize
@throw @try"""

keywords_java = """\
abstract continue for new switch assert default goto package synchronized
boolean do if private this break double implements protected throw byte else
import public throws case enum instanceof return transient catch extends int
short try char final interface static void class finally long strictfp volatile
const float native super while"""

keywords_csharp = """\
abstract add alias as ascending async await base bool break byte case catch char
checked class const continue decimal default delegate descending do double
dynamic else enum event explicit extern false finally fixed float for foreach
from get global goto group if implicit in int interface internal into is join
let lock long namespace new null object operator orderby out override params
partial private protected public readonly ref remove return sbyte sealed select
set short sizeof stackalloc static string struct switch this throw true try
typeof uint ulong unchecked unsafe ushort using value var virtual void volatile
where while yield"""

keywords_javascript = """\
break case catch class const continue debugger default delete do else enum
export extends finally for function if implements import in instanceof interface
let new package private protected return static super switch this throw try
typeof var void while with yield false true null"""

keywords_json = """false true null"""

keywords_python = """\
False None True and as assert break class continue def del elif else except exec
finally for from global if import in is lambda not or pass print raise return
try while with yield"""

keywords_perl = """\
__DATA__ __END__ __FILE__ __LINE__ __PACKAGE__ __SUB__ abs accept alarm and
atan2 AUTOLOAD BEGIN bind binmode bless break caller chdir CHECK chmod chomp
chop chown chr chroot close closedir cmp connect continue CORE cos crypt
dbmclose dbmopen default defined delete DESTROY die do dump each else elsif END
endgrent endhostent endnetent endprotoent endpwent endservent eof EQ eq eval
exec exists exit exp fc fcntl fileno flock for foreach fork format formline GE
ge getc getgrent getgrgid getgrnam gethostbyaddr gethostbyname gethostent
getlogin getnetbyaddr getnetbyname getnetent getpeername getpgrp getppid
getpriority getprotobyname getprotobynumber getprotoent getpwent getpwnam
getpwuid getservbyname getservbyport getservent getsockname getsockopt given
glob gmtime goto grep GT gt hex if index INIT int ioctl join keys kill last lc
lcfirst LE le length link listen local localtime lock log lstat LT lt map mkdir
msgctl msgget msgrcv msgsnd my NE ne next no not NULL oct open opendir or ord
our pack package pipe pop pos print printf prototype push qu quotemeta rand read
readdir readline readlink readpipe recv redo ref rename require reset return
reverse rewinddir rindex rmdir say scalar seek seekdir select semctl semget
semop send setgrent sethostent setnetent setpgrp setpriority setprotoent
setpwent setservent setsockopt shift shmctl shmget shmread shmwrite shutdown sin
sleep socket socketpair sort splice split sprintf sqrt srand stat state study
sub substr symlink syscall sysopen sysread sysseek system syswrite tell telldir
tie tied time times truncate uc ucfirst umask undef UNITCHECK unless unlink
unpack unshift untie until use utime values vec wait waitpid wantarray warn when
while write xor"""

keywords_awk = """\
and ARGC ARGIND ARGV asort asorti atan2 BEGIN bindtextdomain BINMODE break close
compl continue CONVFMT cos dcgettext dcngettext delete do else END ENVIRON ERRNO
exit exp fflush FIELDWIDTHS FILENAME FNR for FS function gensub getline gsub if
IGNORECASE in index int length LINT log lshift match mktime next nextfile NF NR
OFMT OFS or ORS print printf PROCINFO rand return RLENGTH RS rshift RSTART RT
sin split sprintf sqrt srand strftime strtonum sub SUBSEP substr system systime
TEXTDOMAIN tolower toupper while xor"""

keywords_bash = """\
alias ar asa awk banner basename bash bc bdiff break bunzip2 bzip2 cal calendar
case cat cc cd chgrp chmod chown chroot cksum clear cmp col comm compress
continue cp cpio crypt csplit ctags cut date dc dd declare deroff dev df diff
diff3 dir dircmp dircolors dirname do done du echo ed egrep elif else env esac
eval ex exec exit expand export expr factor false fc fgrep fi file find fmt fold
for function functions getconf getopt getopts grep gres groups hash head help
history hostid iconv id if in install integer jobs join kill lc let line link ln
local logname look ls m4 mail mailx make man md5sum mkdir mkfifo mknod more mt
mv newgrp nice nl nm nohup ntps od pack paste patch pathchk pax pcat perl pg
pinky pr print printenv printf ps ptx pwd read readlink readonly red return rev
rm rmdir sed select seq set sh sha1sum shift shred size sleep sort spell split
start stat stop strings strip stty su sum suspend sync tac tail tar tee test
then time times touch tr trap true tsort tty type typeset ulimit umask unalias
uname uncompress unexpand uniq unlink unpack unset until users uudecode uuencode
vdir vi vim vpax wait wc whence which while who whoami wpaste wstart xargs yes
zcat"""

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

keywords_php = """\
__class__ __dir__ __file__ __function__ __line__ __method__ __namespace__
__sleep __wakeup abstract and array as bool boolean break case catch cfunction
class clone const continue declare default die directory do double echo else
elseif empty enddeclare endfor endforeach endif endswitch endwhile eval
exception exit extends false final float for foreach function global goto if
implements include include_once int integer interface isset list namespace new
null object old_function or parent php_user_filter print private protected
public real require require_once resource return static stdclass string switch
this throw true try unset use var while xor"""

keywords_d = """\
abstract alias align asm assert auto body bool break byte case cast catch
cdouble cent cfloat char class const continue creal dchar debug default delegate
delete deprecated do double else enum export extern false final finally float
for foreach foreach_reverse function goto idouble if ifloat import in inout int
interface invariant ireal is lazy long mixin module new null out override
package pragma private protected public real return scope short static struct
super switch synchronized template this throw true try typedef typeid typeof
ubyte ucent uint ulong union unittest ushort version void volatile wchar while
with"""

keywords_verilog = """\
always and assign automatic begin buf bufif0 bufif1 case casex casez cell cmos
config deassign default defparam design disable edge else end endcase endconfig
endfunction endgenerate endmodule endprimitive endspecify endtable endtask event
for force forever fork function generate genvar highz0 highz1 if ifnone incdir
include initial inout input instance integer join large liblist library
localparam macromodule medium module nand negedge nmos nor noshowcancelled not
notif0 notif1 or output parameter pmos posedge primitive pull0 pull1 pulldown
pullup pulsestyle_ondetect pulsestyle_onevent rcmos real realtime reg release
repeat rnmos rpmos rtran rtranif0 rtranif1 scalared showcancelled signed small
specify specparam strong0 strong1 supply0 supply1 table task time tran tranif0
tranif1 tri tri0 tri1 triand trior trireg unsigned use uwire vectored wait
wand weak0 weak1 while wire wor xnor xor"""

keywords_vhdl = """\
access after alias all architecture array assert attribute begin block body
buffer bus case component configuration constant disconnect downto else elsif
end entity exit file for function generate generic group guarded if impure in
inertial inout is label library linkage literal loop map new next null of on
open others out package port postponed procedure process pure range record
register reject report return select severity shared signal subtype then to
transport type unaffected units until use variable wait when while with"""

keywords_r = """\
if else repeat while function for in next break TRUE FALSE NULL NA Inf NaN"""

keywords_yaml = """true false yes no"""

keywords_vala = """\
abstract as base bool break case catch char class const construct continue
default delegate delete do dynamic else ensures enum errordomain extern false
finally for foreach generic get if in int interface keywordclass2.vala=namespace
lock new null out override owned private protected public ref requires return
set signal sizeof static string struct switch this throw throws true try typeof
unowned using value var virtual weak while yield yields"""

keywords_go = """\
bool break byte case chan complex128 complex64 const continue default defer else
fallthrough false float32 float64 for func go goto if import int int16 int32
int64 int8 interface len map nil package range return select string struct
switch true type uint uint16 uint32 uint64 uint8 uintptr var"""

keywords_pike = """\
array break case catch class constant continue do else enum float for foreach
function if import inherit int lambda mapping mixed multiset object program
return static string switch typeof void while"""

keywords_idl = """\
__int3264 __int64 aggregatable allocate appobject arrays async async_uuid
attribute auto_handle bindable boolean broadcast byte byte_count call_as
callback char coclass code comm_status const context_handle
context_handle_noserialize context_handle_serialize control cpp_quote
custom decode default defaultbind defaultcollelem defaultvalue defaultvtable
dispinterface displaybind dllname double dual enable_allocate encode endpoint
entry enum error_status_t explicit_handle fault_status first_is float handle
handle_t heap helpcontext helpfile helpstring helpstringcontext helpstringdll
hidden hyper id idempotent ignore iid_as iid_is immediatebind implicit_handle
import importlib in in_line include inout int interface last_is lcid length_is
library licensed local long max_is maybe message methods midl_pragma
midl_user_allocate midl_user_free min_is module ms_union native ncacn_at_dsp
ncacn_dnet_nsp ncacn_http ncacn_ip_tcp ncacn_nb_ipx ncacn_nb_nb ncacn_nb_tcp
ncacn_np ncacn_spx ncacn_vns_spp ncadg_ip_udp ncadg_ipx ncadg_mq ncalrpc nocode
nonbrowsable noncreatable nonextensible noscript notify object odl oleautomation
optimize optional out out_of_line pipe pointer_default pragma properties propget
propput propputref ptr public range readonly ref represent_as requestedit
restricted retval scriptable shape shared short signed size_is small source
strict_context_handle string struct switch switch_is switch_type transmit_as
typedef uidefault union unique unsigned user_marshal usesgetlasterror uuid
v1_enum vararg version void wchar_t wire_marshal wstring"""

keywords_matlab = """\
break case catch continue else elseif end for function global if otherwise
persistent return switch try while"""

keywords_octave = """\
__FILE__ __LINE__ break case catch classdef continue do else elseif end
end_try_catch end_unwind_protect endclassdef endenumeration endevents endfor
endif endmethods endparfor endproperties endswitch endwhile enumeration events
for function endfunction get global if methods otherwise parfor persistent
properties return set static switch try until unwind_protect
unwind_protect_cleanup while"""

keywords_postscript = """\
$error = == FontDirectory StandardEncoding UserObjects abs add aload
anchorsearch and arc arcn arcto array ashow astore atan awidthshow begin bind
bitshift bytesavailable cachestatus ceiling charpath clear cleardictstack
cleartomark clip clippath closefile closepath concat concatmatrix copy copypage
cos count countdictstack countexecstack counttomark currentcmykcolor
currentcolorspace currentdash currentdict currentfile currentflat currentfont
currentgray currenthsbcolor currentlinecap currentlinejoin currentlinewidth
currentmatrix currentmiterlimit currentpagedevice currentpoint currentrgbcolor
currentscreen currenttransfer cvi cvlit cvn cvr cvrs cvs cvx def defaultmatrix
definefont dict dictstack div dtransform dup echo end eoclip eofill eq erasepage
errordict exch exec execstack executeonly executive exit exp false file fill
findfont flattenpath floor flush flushfile for forall ge get getinterval
grestore grestoreall gsave gt idetmatrix idiv idtransform if ifelse image
imagemask index initclip initgraphics initmatrix inustroke invertmatrix
itransform known kshow le length lineto ln load log loop lt makefont mark matrix
maxlength mod moveto mul ne neg newpath noaccess nor not null nulldevice or
pathbbox pathforall pop print prompt pstack put putinterval quit rand rcheck
rcurveto read readhexstring readline readonly readstring rectstroke repeat
resetfile restore reversepath rlineto rmoveto roll rotate round rrand run save
scale scalefont search setblackgeneration setcachedevice setcachelimit
setcharwidth setcolorscreen setcolortransfer setdash setflat setfont setgray
sethsbcolor setlinecap setlinejoin setlinewidth setmatrix setmiterlimit
setpagedevice setrgbcolor setscreen settransfer setvmthreshold show showpage sin
sqrt srand stack start status statusdict stop stopped store string stringwidth
stroke strokepath sub systemdict token token transform translate true truncate
type ueofill undefineresource userdict usertime version vmstatus wcheck where
widthshow write writehexstring writestring xcheck xor"""

keywords_cmake = """\
add_custom_command add_custom_target add_definitions add_dependencies
add_executable add_library add_subdirectory add_test aux_source_directory
build_command build_name cmake_minimum_required configure_file
create_test_sourcelist else elseif enable_language enable_testing endforeach
endif endmacro endwhile exec_program execute_process export_library_dependencies
file find_file find_library find_package find_path find_program fltk_wrap_ui
foreach get_cmake_property get_directory_property get_filename_component
get_source_file_property get_target_property get_test_property if include
include_directories include_external_msproject include_regular_expression
install install_files install_programs install_targets link_directories
link_libraries list load_cache load_command macro make_directory
mark_as_advanced math message option output_required_files project qt_wrap_cpp
qt_wrap_ui remove remove_definitions separate_arguments set
set_directory_properties set_source_files_properties set_target_properties
set_tests_properties site_name source_group string subdir_depends subdirs
target_link_libraries try_compile try_run use_mangled_mesa utility_source
variable_requires vtk_make_instantiator vtk_wrap_java vtk_wrap_python
vtk_wrap_tcl while write_file"""

syntax_plain = Syntax("plain", "Plain Text", stc.STC_LEX_NULL, "*")

syntax_list = [
    Syntax("c", "C", stc.STC_LEX_CPP, "*.c;*.h", "//", keywords_c),
    Syntax("cpp", "C++", stc.STC_LEX_CPP, "*.cpp;*.cxx;*.cc;*.hpp;*.hxx;*.hh", "//", keywords_cpp),
    Syntax("objc", "Objective-C", stc.STC_LEX_CPP, "*.m", "//", keywords_c + keywords_objc),
    Syntax("objcpp", "Objective-C++", stc.STC_LEX_CPP, "*.mm", "//", keywords_cpp + keywords_objc),
    Syntax("java", "Java", stc.STC_LEX_CPP, "*.java;*.jad;*.pde", "//", keywords_java),
    Syntax("csharp", "C#", stc.STC_LEX_CPP, "*.cs", "//", keywords_csharp),
    Syntax("javascript", "JavaScript", stc.STC_LEX_CPP, "*.js;*.es", "//", keywords_javascript),
    Syntax("json", "JSON", stc.STC_LEX_CPP, "*.json", "//", keywords_json),
    Syntax("python", "Python", stc.STC_LEX_PYTHON, "*.py", "#", keywords_python),
    Syntax("html", "HTML", stc.STC_LEX_HTML, "*.html;*.htm"),
    Syntax("sgml", "SGML", stc.STC_LEX_HTML, "*.sgml"),
    Syntax("xml", "XML", stc.STC_LEX_XML, "*.xml;*.xhtml;*.xht;*.xslt;*.rdf;*.rss;*.atom;*.svg;*.dbk;*.kml"),
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
    Syntax("php", "PHP", stc.STC_LEX_PHPSCRIPT, "*.php;*.php3;*.phtml", "//", keywords_php),
    Syntax("d", "D", stc.STC_LEX_D, "*.d", "//", keywords_d),
    Syntax("verilog", "Verilog", stc.STC_LEX_VERILOG, "*.v;*.vh", "//", keywords_verilog),
    Syntax("vhdl", "VHDL", stc.STC_LEX_VHDL, "*.vhd;*.vhdl", "", keywords_vhdl),
    Syntax("r", "R", stc.STC_LEX_R, "*.r;*.rsource;*.s", "#", keywords_r),
    Syntax("yaml", "YAML", stc.STC_LEX_YAML, "*.yaml;*.yml", "#", keywords_yaml),
    Syntax("vala", "Vala", stc.STC_LEX_CPP, "*.vala", "//", keywords_vala),
    Syntax("go", "Go", stc.STC_LEX_CPP, "*.go", "//", keywords_go),
    Syntax("pike", "Pike", stc.STC_LEX_CPP, "*.pike", "//", keywords_pike),
    Syntax("idl", "IDL", stc.STC_LEX_CPP, "*.idl;*.odl", "//", keywords_idl),
    Syntax("octave", "Octave", stc.STC_LEX_OCTAVE, "*.m;*.m.octave", "#", keywords_octave),
    Syntax("matlab", "Matlab", stc.STC_LEX_MATLAB, "*.m", "%", keywords_matlab),
    Syntax("postscript", "PostScript", stc.STC_LEX_PS, "*.ps", "%", keywords_postscript),
    Syntax("cmake", "CMake", stc.STC_LEX_CMAKE, "CMakeLists.txt;*.cmake;*.cmake.in;*.ctest;*.ctest.in", "#", keywords_cmake),
    syntax_plain,
]

syntax_dict = dict((syntax.name, syntax) for syntax in syntax_list)

def syntax_from_filename(filename):
    for syntax in syntax_list:
        if syntax.file_regex.match(os.path.basename(filename)):
            return syntax
    return syntax_plain
