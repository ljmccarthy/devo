import wx.stc

ident = "java"
name = "Java"
extensions = ["*.java"]
lexer = wx.stc.STC_LEX_CPP
indent = 4
use_tabs = False
comment_token = "//"

from cpp import stylespecs

# http://docs.oracle.com/javase/tutorial/java/nutsandbolts/_keywords.html

keywords = """\
abstract  continue  for  new  switch
assert  default  goto  package  synchronized
boolean  do  if  private  this
break  double  implements  protected  throw
byte  else  import  public  throws
case  enum  instanceof  return  transient
catch  extends  int  short  try
char  final  interface  static  void
class  finally  long  strictfp  volatile
const  float  native  super  while
"""
