# taky-lookingglass
A time series project for Taky in order to have a centralilzed stored CoT Database to search through

### TODO
- [ ] Filter out anything but the End User Devices
- [ ] Format and store the COTs in a MariaDB Docker
- [ ] Create a FIFO Queue for the ingest COTs to handle spikes of data
- [ ] Create a thread in order to have concurrent PUTs into the SQL DB
- [ ] Grafana
    - [ ] Create a dashboard
    - [ ] Configure provisioning in grafana
- [ ] Create a global working docker-compose.yml
- [ ] Clean up code
- [ ] Create a README and Documentation