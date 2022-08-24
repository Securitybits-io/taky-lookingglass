# taky-lookingglass
A time series project for Taky in order to have a centralilzed stored CoT Database to search through

### TODO
- [ ] Create a CoT Whitelist to have user input filter the queue
- [ ] Format and store the COTs in a MariaDB Docker
- [ ] Create a FIFO Queue for the ingest COTs to handle spikes of data
- [x] Create a thread in order to Ingest COTs
- [ ] Create a Thread for outgoing CoTs
- [ ] Create environment variables
    - [ ] for whitelist of CoT types
    - [ ] if Color rewrite
    - [ ] Server Name (NATO/OPFOR/REDFOR), that will be ingested into the database
    - [ ] SQL Connection Details
    - [ ] TAKY server connection details
    - [ ] grafana SQL user and password for reading the database
- [ ] Grafana
    - [ ] Create a dashboard
    - [ ] Configure provisioning in grafana
- [ ] SQL
    - [ ] Connect function
    - [x] Create TAKYCot Database
    - [x] Create grafana user with password with read only
- [ ] Create a global working docker-compose.yml
- [ ] Clean up code
- [ ] Create a README and Documentation

## DOCS
- https://superfastpython.com/thread-queue/