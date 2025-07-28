# Congressional Voting Data APIs: Comprehensive Analysis

The landscape for congressional voting data APIs has shifted significantly in 2025, with one major service discontinued and another newly launched. Of the four APIs examined, only two provide meaningful access to structured congressional voting data for your legislative tracking platform.

## API Status Overview 

**Congress.gov API** emerges as the primary viable option, having launched beta House roll call voting endpoints in May 2025. **ProPublica's Congress API was permanently discontinued in February 2025**, eliminating what was previously the most comprehensive voting data source. The **Federal Register API** contains no congressional voting data, while **GovInfo API** offers only limited document-based access requiring extensive text parsing.

## Detailed API Capabilities

### Congress.gov API: The New Standard

**Coverage and Data Types**: The Congress.gov API now provides **structured House roll call voting data from 2023 forward** through dedicated endpoints. It includes final passage votes, roll call records, vote counts, and individual member votes with BioGuide IDs for standardization. However, **Senate roll call endpoints are not yet available** and committee votes remain inaccessible as structured data.

**Member-by-Member Records**: The API delivers complete individual voting records for House members, including vote positions (Yea, Nay, Present, Not Voting), party affiliation, and state representation. Each member is identified through standardized BioGuide IDs, enabling consistent tracking across legislative sessions.

**Data Structure and Format**: Responses come in JSON (recommended), XML, or JSONP formats with comprehensive metadata. The API provides vote results, party breakdowns, timestamps, and direct links to official vote records. Rate limiting is set at **5,000 requests per hour** with daily updates typically occurring the morning after sessions adjourn.

**Key Limitations**: The most significant gap is **absence of Senate voting data**, creating a major blind spot for comprehensive legislative tracking. Historical coverage is limited to recent Congresses (2023+), and committee votes are not available as structured data. Voice votes and division votes are not tracked by any official source.

### ProPublica Congress API: No Longer Available

**Discontinued Service**: The ProPublica Congress API was **archived and discontinued in February 2025**, with no new API keys available. This represents a major loss for the congressional data ecosystem, as it previously provided the most comprehensive voting data available.

**Historical Capabilities**: When active, the API offered extensive voting data coverage from 1989 (Senate) and 1991 (House) with member-by-member positions updated every 30 minutes. It included party breakdowns, voting analysis tools, and tracked missed votes and party unity statistics. The service provided both individual member positions and aggregate vote totals in well-structured JSON format.

### GovInfo API: Limited Document Access

**Document Repository Only**: The GovInfo API serves as a document repository rather than a structured voting data service. While it provides access to Congressional Record documents containing voting information, **it offers no structured roll call vote records, vote tallies, or member-by-member breakdowns**.

**Search Capabilities**: Developers can search for voting-related documents using metadata fields like `memberyes:`, `memberno:`, and `votenumber:`, but extracting meaningful voting data requires parsing unstructured text from Congressional Record documents. Historical coverage extends from 1994 to present with daily updates.

### Federal Register API: Not Applicable

**No Congressional Data**: The Federal Register API is **completely unsuitable for congressional voting data**, as it exclusively covers executive branch documents including rules, regulations, and presidential materials. It provides no legislative voting records, bill tracking capabilities, or member information.

**Complementary Value**: While useless for voting data, the API could serve as a complementary resource for tracking regulatory implementation of congressional legislation and executive responses to legislative actions.

## Comprehensive Comparison Matrix

| Feature | Congress.gov | ProPublica | Federal Register | GovInfo |
|---------|-------------|------------|------------------|---------|
| **Availability** | Active | **Discontinued** | Active | Active |
| **House Votes** | Yes (2023+) | Was comprehensive | No | Document only |
| **Senate Votes** | **Not yet** | Was comprehensive | No | Document only |
| **Member Records** | Complete | Was complete | No | Unstructured |
| **Historical Data** | Limited | Was extensive | No | 1994+ documents |
| **Update Frequency** | Daily | Was 30 minutes | Daily | Daily |
| **Rate Limits** | 5,000/hour | Was 5,000/day | None | 40/hour |

## Implementation Recommendations

### Primary Architecture Strategy

**Use Congress.gov API as the foundation** for your legislative tracking platform, supplemented by alternative sources for Senate data. The recent launch of House roll call endpoints provides official, structured voting data with member-by-member records and proper authentication through free API keys.

**Address Senate Data Gap**: Since Congress.gov lacks Senate voting endpoints, consider integrating **GovTrack.us API** or **Voteview.com** for Senate voting data. These services provide historical Senate voting records and can bridge the coverage gap until official Senate endpoints become available.

**Data Processing Requirements**: Implement robust pagination handling for Congress.gov API (limited to 250 results per request) and plan for rate limit management across 5,000 hourly requests. Build caching layers for frequently accessed voting data and prepare for varying data completeness across different Congress periods.

### Technical Implementation Considerations

**API Integration**: Congress.gov requires API key authentication through api.data.gov with straightforward REST endpoints returning JSON responses. The standardized BioGuide ID system ensures consistent member identification across different data sources and legislative sessions.

**Performance Optimization**: Given the daily update frequency, implement efficient polling schedules rather than continuous monitoring. The API's production-ready status (no longer beta) provides reliability for commercial applications, though developers should handle historical data variations gracefully.

**Error Handling**: Plan for missing data scenarios, particularly for historical votes and incomplete member information. The API's structured error responses and clear documentation facilitate robust error handling implementation.

## Current Data Ecosystem Reality

The discontinuation of ProPublica's comprehensive Congress API represents a significant loss for the congressional data ecosystem. **Congress.gov API now serves as the primary official source** for structured voting data, though its current House-only coverage creates implementation challenges for comprehensive legislative tracking.

For building a congressional bill and executive order tracking website, your best approach combines Congress.gov API for official House voting data with alternative sources for Senate coverage. This hybrid architecture addresses the current API landscape limitations while positioning your platform to leverage future Congress.gov expansions when Senate endpoints become available.

The Federal Register API serves as a valuable complement for tracking regulatory implementation of congressional legislation but provides no direct voting data capabilities. GovInfo API remains useful for document retrieval and full-text Congressional Record access but requires significant text processing overhead for extracting structured voting information.