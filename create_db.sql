drop table if exists Clues;
CREATE TABLE Clues (
    clue_id int NOT NULL PRIMARY KEY IDENTITY,
    clue varchar(255) NOT NULL,
    answer varchar(255) NOT NULL,
    answer_len int NOT NULL,
    date date NOT NULL,
    weekday int NOT NULL
);