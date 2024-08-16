DROP TABLE IF EXISTS sqlzilla.examples
GO

CREATE TABLE IF NOT EXISTS sqlzilla.examples (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    prompt VARCHAR(255) NOT NULL,
    query VARCHAR(255) NOT NULL,
    schema_name VARCHAR(255) NOT NULL
)
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('List all aircrafts.', 'SELECT * FROM Aviation.Aircraft', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('Find all incidents for the aircraft with ID ''N12345''.', 'SELECT * FROM Aviation.Event WHERE EventId IN (SELECT EventId FROM Aviation.Aircraft WHERE ID = ''N12345''', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('List all incidents in the ''Commercial'' operation type.', 'SELECT * FROM Aviation.Event WHERE EventId IN (SELECT EventId FROM Aviation.Aircraft WHERE OperationType = ''Commercial''', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('Find the total number of incidents.', 'SELECT COUNT(*) FROM Aviation.Event', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('List all incidents that occurred in ''Canada''.', 'SELECT * FROM Aviation.Event WHERE LocationCountry = ''Canada''', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('How many incidents are associated with the aircraft with AircraftKey 5?', 'SELECT COUNT(*) FROM Aviation.Aircraft WHERE AircraftKey = 5', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('Find the total number of distinct aircrafts involved in incidents.', 'SELECT COUNT(DISTINCT AircraftKey) FROM Aviation.Aircraft', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('List all incidents that occurred after 5 PM.', 'SELECT * FROM Aviation.Event WHERE EventTime > 1700', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('Who are the top 5 operators by the number of incidents?', 'SELECT TOP 5 OperatorName, COUNT(*) AS IncidentCount FROM Aviation.Aircraft GROUP BY OperatorName ORDER BY IncidentCount DESC', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('Which incidents occurred in the year 2020?', 'SELECT * FROM Aviation.Event WHERE YEAR(EventDate) = 2020', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('What was the month with most events in the year 2020?', 'SELECT TOP 1 MONTH(EventDate) EventMonth, COUNT(*) EventCount FROM Aviation.Event WHERE YEAR(EventDate) = 2020 GROUP BY MONTH(EventDate) ORDER BY EventCount DESC', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('How many crew members were involved in incidents?', 'SELECT COUNT(*) FROM Aviation.Crew', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('List all incidents with detailed aircraft information for incidents that occurred in the year 2012.', 'SELECT e.EventId, e.EventDate, a.AircraftManufacturer, a.AircraftModel, a.AircraftCategory FROM Aviation.Event e JOIN Aviation.Aircraft a ON e.EventId = a.EventId WHERE Year(e.EventDate) = 2012', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('Find all incidents where there were more than 5 injuries and include the aircraft manufacturer and model.', 'SELECT e.EventId, e.InjuriesTotal, a.AircraftManufacturer, a.AircraftModel FROM Aviation.Event e JOIN Aviation.Aircraft a ON e.EventId = a.EventId WHERE e.InjuriesTotal > 5', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('List all crew members involved in incidents with serious injuries, along with the incident date and location.', 'SELECT c.CrewNumber, c.Age, c.Sex, e.EventDate, e.LocationCity, e.LocationState FROM Aviation.Crew c JOIN Aviation.Event e ON c.EventId = e.EventId WHERE c.Injury = ''Serious''', 'Aviation')
GO

INSERT INTO sqlzilla.examples (prompt, query, schema_name) VALUES ('sales by category', 'SELECT TOP 3 p."Category", SUM(t."AmountOfSale") AS total_sales FROM HoleFoods.SalesTransaction t JOIN HoleFoods.Product p ON t."Product" = p."ID" GROUP BY p."Category" ORDER BY total_sales DESC;', 'HoleFoods')
GO
