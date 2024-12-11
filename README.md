# Crossword Helper

Visit site [here](https://proud-glacier-fd31f2a327ad4a17ba0bd17775346534.azurewebsites.net/)

Crossword clues are stored in Azure SQL Database, with a Azure Function appending the newest crossword's clues daily. The app is ran using Azure App Service.

Home Page: View most popular crossword clue-answer pairs of all time, and most popular answers of all time.
Select Date: For a specific date, view most popular crossword clue-answer pairs of all time that appear in that day's crossword, and most popular answers of all time that appear in that day's crossword.
Search for clue: Using substring matching, search for most popular clue-answer pairs for a given keyword string.
Search for answer: Using exact string matching, search for most popular clue-answer pairs for a given answer.
