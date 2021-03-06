# coding=UTF8

import datetime

name = "Devo"

release_date = datetime.date(2016, 5, 18)

version = (1, 4, 0)

version_string = ".".join(str(x) for x in version)

identifier = "com.iogopro.devo"

copyright = u"Copyright © 2010-%s Luke McCarthy" % release_date.year

developer = "Developer: Luke McCarthy <luke@iogopro.co.uk>"

company_name = "Iogopro Software"

url = "https://github.com/shaurz/devo"

bug_report_url = "https://github.com/shaurz/devo/issues"

latest_release_url = "https://github.com/shaurz/devo/releases/latest"
