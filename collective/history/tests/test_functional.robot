*** Settings ***

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Test Setup  Open test browser
Test Teardown  Close all browsers

*** Test Cases ***

Create content and check history is working
    Given I'm logged in as the site owner 
    
     When I add a folder 'My folder'
      And I add and publish a document 'Test document'
      And I rename the content's title of 'test-document' to 'New document title'
      And I remove the content 'test-document'
      And I go to the history
    
     Then The history table row '1' should contain 'created' for '/my-folder'
      And The history table row '2' should contain 'created' for '/test-document'
      And The history table row '3' should contain 'statechanged' for '/test-document'
      And The history table row '4' should contain 'modified' for '/test-document'
      And The history table row '5' should contain 'deleted' for '/test-document'


Create a dexterity content type, use it and check history
    Given I'm logged in as the site owner
      And Dexterity is activated

     When I create a dexterity content type 'mytype' called 'MyType'
      And I add a dexterity content 'mytype' named 'Test my type'
      And I rename the content's title of 'test-my-type' to 'New title'
      And I remove the content 'test-my-type'
      And I go to the history

     Then The history table row '1' should contain 'created' for '/test-my-type'
      And The history table row '2' should contain 'statechanged' for '/test-my-type'
      And The history table row '3' should contain 'modified' for '/test-my-type'
      And The history table row '4' should contain 'deleted' for '/test-my-type'


Create and delete a comment and check history
    Given I'm logged in as the site owner
      And Discussion is activated

     When I add and publish a document 'Test document'
      And I enable comments on document 'test-document'
      ${comment_id} =  And I add a comment 'Coucou'
      And I delete a comment '${comment_id}'
      And I go to the history

     Then The history table row '1' should contain 'created' for '/test-document'
      And The history table row '2' should contain 'statechanged' for '/test-document'
      And The history table row '3' should contain 'edited' for '/test-document'
      And The history table row '4' should contain 'added' for '/test-document/++conversation++default/${comment_id}'
      And The history table row '5' should contain 'removed' for '/test-document/++conversation++default/${comment_id}'


*** Keywords ***

My Rename Content Title
    [arguments]  ${id}  ${new_title}

    Go to  ${PLONE_URL}/${id}/object_rename
    Input Text for sure  css=input#${id}_title  ${new_title}
    Click Button  Rename All
    Go to  ${PLONE_URL}/${id}

I'm logged in as the site owner
    Log in as site owner
    Go to homepage

The history table row '${row}' should contain '${what}' for '${where}'
    Table Row Should Contain    history  ${row}  /${PLONE_SITE_ID}${where}
    Table Row Should Contain    history  ${row}  ${what}

I go to the history
    Go to  ${PLONE_URL}/portal_history

I add a folder '${folder}'
    Add folder    ${folder}

I add and publish a document '${document}'
    Add document	${document}
    Workflow Publish

I rename the content's title of '${content}' to '${title}'
    My Rename Content Title    ${content}  ${title}
    Wait Until Page Contains Element  css=body.section-${content}

I remove the content '${content}'
    Remove Content    ${content}

Dexterity is activated
    Go to  ${PLONE_URL}/prefs_install_products_form
    Select Checkbox  css=#plone\\.app\\.dexterity
    Click Button  Activate
    Wait Until Page Contains Element  css=#plone\\.app\\.dexterity

I create a dexterity content type '${id}' called '${name}'
    Go to  ${PLONE_URL}/@@dexterity-types/@@add-type
    Input Text  name=form.widgets.title  ${name}
    Input Text  name=form.widgets.id  ${id}
    Click Button  Add
    Go to homepage

I add a dexterity content '${id}' named '${title}'
    Go to  ${PLONE_URL}/++add++${id}
    Wait Until Page Contains Element  css=#form-widgets-IDublinCore-title
    Input Text  css=#form-widgets-IDublinCore-title  ${title}
    Click Button  Save
    Workflow Publish

Discussion is activated
    Go to  ${PLONE_URL}/@@discussion-settings
    Select Checkbox  css=#form-widgets-globally_enabled-0
    Click Button  Save
    Go to homepage

I enable comments on document '${document}'
    Go to  ${PLONE_URL}/${document}/edit#fieldsetlegend-settings
    Select Checkbox  css=#allowDiscussion
    Click Button  Save
    Go to  ${PLONE_URL}/${document}

I add a comment '${comment}'
    Input text and validate  css=#form-widgets-comment-text  ${comment}
    Click Button  Comment
    ${comment_id} =  Get Element Attribute  css=.comment:last-of-type@id
    [Return]  ${comment_id}

I delete a comment '${comment}'
    Click Button  Delete