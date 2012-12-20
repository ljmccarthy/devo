# coding=UTF8

import datetime

name = "Devo"

release_date = datetime.date(2012, 12, 21)

version = (1, 0, 0)

version_string = ".".join(str(x) for x in (version if version[2] != 0 else version[:2]))

identifier = "com.iogopro.devo"

copyright = u"Copyright © 2010-2012 Luke McCarthy"

developer = "Developer: Luke McCarthy <luke@iogopro.co.uk>"

company_name = "Iogopro Software"

url = "http://iogopro.com/devo"
