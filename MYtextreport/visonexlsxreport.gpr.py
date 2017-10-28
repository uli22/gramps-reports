#------------------------------------------------------------------------
#
# SourcesCitations Report
#
#------------------------------------------------------------------------

plg = newplugin()
plg.id    = 'visonexlsxreport'
plg.name  = _("VISONE XLSX")
plg.description =  _("Provides a report for Excel")
plg.version = '1.0'
plg.gramps_target_version = '4.2'
plg.status = STABLE
plg.fname = 'visonexlsxreport.py'
plg.ptype = REPORT
plg.authors = ["Uli22"]
plg.authors_email = ["hansulrich.frink@gmail.com"]
plg.category = CATEGORY_TEXT
plg.reportclass = 'VisoneXLSXReport'
plg.optionclass = 'VisoneXLSXReportOptions'
plg.report_modes = [REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI]
plg.require_active = False