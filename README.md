# Extract LinkedIn Contact

Extract contact informations of the persons page from a lLinkedIn company page and export it in an excel file.
The script use Selenium to connect an existing account to LinkedIn, go to the company page and scrap all profiles related to the company.
All profiles are converted to a filtered Pandas dataframe and exported to an Excel file named from the `ID_page_linked_in`.

`postes_cibles` - Array of terms to be in job_titles

`termes_a_exclure` - Array of terms to exclude from the lit

use in command line : 
`python get_linkedin_contact.py <ID_page_linked_in> <login_linkedin> <password_linkedin>`⌢琠歩潴⵫捳慲灰牥•਍