Refer to the following guidelines to ensure efficient pull requests and code reviews:
- [Pull Requests](https://dev.azure.com/RioTintoDevOps/Analytics%20and%20Data%20Engineering%20Portfolio/_wiki/wikis/Analytics-and-Data-Engineering-Portfolio.wiki/11431/Pull-Requests) 
- [Code Reviews](https://dev.azure.com/RioTintoDevOps/Analytics%20and%20Data%20Engineering%20Portfolio/_wiki/wikis/Analytics-and-Data-Engineering-Portfolio.wiki/11433/Code-Reviews)

### Ticket Reference [TicketNumber](Link)
<!--Attach a hyperlink to your ADO ticket.-->

## Description

**Motivation & Context**  
<!-- Explain why this change was made (e.g. the problem it solves and/or the value it adds). -->

**List of Changes**  
<!-- Include a summary of the changes made. -->

**Supporting Materials (if applicable)**  
<!-- Include links to relevant notebook files, diagrams or documentation to make reviewing easier. -->

**Dependencies (if applicable)**  
<!-- List any dependencies that are required for this change. -->

**Reviewer Notes (if applicable)**  
<!-- Highlight anything you want reviewers to scrutinise closely. -->

## Type of Change
<!-- 
Please delete options that are not relevant.
-->

- Bug fix (non-breaking change which fixes an issue)
- New feature (non-breaking change which adds functionality)
- Breaking change (fix or feature that would cause existing functionality to not work as expected)
- This change requires a documentation update

## How Has This Been Tested?
<!--
Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Please also list any relevant details for your test configuration
- Test A
- Test B
-->

## Checklist

**PR Quality & Process**
- [ ] My PR is small, focused and self-contained, modifying only the lines and files required for this change.
- [ ] I have written a clear and descriptive summary of my PR.
- [ ] I have pre-reviewed my PR.
- [ ] I have selected appropriate reviewers.
- [ ] I understand that code reviews are a shared safety net, not personal feedback.

**Code Quality**
- [ ] I have performed a self-review of my code.
- [ ] My code follows the style guidelines of this project.
- [ ] My code is clean and free of temporary debugging statements.
- [ ] I have refactored the code, particularly in hard-to-understand areas.
- [ ] My changes generate no new warnings.
- [ ] I have covered logging functionality for my changes.

**Testing**
- [ ] I have tested my changes to ensure they work as expected and do not break existing functionality.
- [ ] Where applicable, I have added or updated tests that prove my bug fix or new feature works.
- [ ] New and existing tests pass locally with my changes.
- [ ] All relevant tests (unit, integration, UI, API, etc.) pass successfully.
- [ ] My changes do not break deployment (if applicable).

**Documentation & Tracking**
- [ ] I have made corresponding changes to the documentation.
- [ ] I have updated the ADO ticket with progress and relevant links.

**Dependencies & Build**
- [ ] I have updated dependency files (e.g. Pipfile or Poetry file) if required.
- [ ] Any dependent changes have been merged and published in downstream modules.
- [ ] I have converted notebooks to Python scripts if required.

**Container & Pipeline**
- [ ] I have built the container image successfully locally.
- [ ] I have validated the ARM template locally with appropriate parameters.
- [ ] I have configured the pipeline YAML file(s) correctly.
- [ ] I have properly defined container environment variables.
- [ ] I have updated documentation to reflect the deployment process.

**Security**
- [ ] I have ensured all secrets are properly managed (e.g. stored in Key Vault, not hardcoded).

**Git & Commits**
- [ ] My commit history is short and clean, with one commit per task.
- [ ] I will squash every fix I make post team review before merging.
    > If using `dev` branch: I will squash and merge my branch into `dev` then merge `dev` into `main`.
- [ ] I will delete my branch after the PR has been merged.

## Screenshots (if applicable)
Include relevant screenshots that help reviewers understand the change or verify its impact.