# taky-lookingglass
A time series project for Taky in order to have a centralilzed stored CoT Database to search through

### TODO
- [ ] Create a CoT Whitelist to have user input filter the queue
- [x] Format and store the COTs in a MariaDB Docker
- [x] Create a FIFO Queue for the ingest COTs to handle spikes of data
- [x] Create a thread in order to Ingest COTs
- [x] Create a Thread for outgoing CoTs
- [ ] Create environment variables
    - [ ] for whitelist of CoT types
    - [ ] if Color rewrite
    - [ ] Server Name (NATO/OPFOR/REDFOR), that will be ingested into the database
    - [ ] SQL Connection Details
    - [x] TAKY server connection details
    - [x] grafana SQL user and password for reading the database
- [x] Grafana
    - [x] Create a dashboard
    - [x] Configure provisioning in grafana
- [x] SQL
    - [x] Connect function
    - [x] Create TAKYCot Database
    - [x] Create grafana user with password with read only
- [x] Create a global working docker-compose.yml
- [x] Clean up code
- [ ] Create a README and Documentation

## DOCS
- https://superfastpython.com/thread-queue/