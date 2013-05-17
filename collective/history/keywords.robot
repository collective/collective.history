*** Keywords ***

Go to history
    Go to  ${PLONE_URL}/portal_history

Verify history
    [Arguments]  ${row}  ${what}  ${where}
    Table Row Should Contain    history  ${row}  /${PLONE_SITE_ID}${where}
    Table Row Should Contain    history  ${row}  ${what}
