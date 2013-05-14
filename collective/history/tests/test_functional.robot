*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Create content and check history is working
    Log in as site owner
    Go to homepage
    Add folder    My folder
    Add document    Test document
    Workflow Publish
    Rename Content Title    test-document  New document title
    Wait Until Page Contains Element  css=body.section-test-document
    Remove Content    test-document
    Go to history
    Verify history    1   created       /my-folder
    Verify history    2   created       /test-document
    Verify history    3   statechanged  /test-document
    Verify history    4   modified      /test-document
    Verify history    5   deleted       /test-document

Create a dexterity content type, use it and check history
    Log in as site owner
    Create a dexterity content type    mytype  MyType
    Add dexterity  mytype  Test my type
    Workflow Publish
    Rename Content Title    test-my-type  New title
    Wait Until Page Contains Element    css=body.section-test-my-type
    Remove Content    test-my-type
    Go to history
    Verify history    1   created       /test-my-type
    Verify history    2   statechanged  /test-my-type
    Verify history    3   modified      /test-my-type
    Verify history    4   deleted       /test-my-type

*** Keywords ***

Go to history
    Go to  ${PLONE_URL}/portal_history

Verify history
    [Arguments]  ${row}  ${what}  ${where}
    Table Row Should Contain    history  ${row}  /${PLONE_SITE_ID}${where}
    Table Row Should Contain    history  ${row}  ${what}

Create a dexterity content type
    [Arguments]  ${id}  ${name}
    Go to  ${PLONE_URL}/prefs_install_products_form
    Select Checkbox  css=#plone\\.app\\.dexterity
    Click Button  Activate
    Wait Until Page Contains Element  css=#plone\\.app\\.dexterity
    Go to  ${PLONE_URL}/@@dexterity-types/@@add-type
    Input Text  name=form.widgets.title  ${name}
    Input Text  name=form.widgets.id  ${id}
    Click Button  Add
    Go to  ${PLONE_URL}

Add dexterity
    [Arguments]  ${id}  ${title}
    Go to  ${PLONE_URL}/++add++${id}
    Wait Until Page Contains Element  css=#form-widgets-IDublinCore-title
    Input Text  css=#form-widgets-IDublinCore-title  ${title}
    Click Button  Save
