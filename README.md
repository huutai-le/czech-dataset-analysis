# Project Background
This project analyzes customer banking behavior and loan repayment risk using the Berka Banking Dataset, a financial dataset that simulates the operations of a retail bank. The bank provides services such as savings accounts, credit cards, loans, and payment orders to customers across multiple districts.

The primary business objective is to better understand customer financial behavior and identify early warning signals for risky loans. This aligns closely with modern banking priorities such as customer retention, risk management, and portfolio health monitoring.

Insights and recommendations are provided on the following key areas:

- Customer Value & Engagement
- Banking Transaction Behavior
- Regional Financial Risk
- Loan Risk Analytics

The Python code used to inspect and clean the data for this analysis can be found here [link].

Target Python code for creating dim/fact tables regarding various business questions can be found here [link].

An interactive Power BI dashboard used to report and explore banking trends can be found here [link].

# Data Structure & Architecture

The Berka Banking Dataset as seen below consists of eight tables transformed into dimensional and fact tables using a star schema design.

- 4500 account records
- 5369 client records
- 5369 disposition records
- 6471 permanent order records
- 1056320 transaction records
- 682 loan records
- 892 credit card records
- 77 demographic data records

Detailed information about the columns can be found here [link].

<img width="507" height="298" alt="image" src="https://github.com/user-attachments/assets/01e97b71-5514-47f9-9c35-5c20512c9105" />

The project focuses on building an architecture pipeline for analytics and prediction:

<img width="985" height="485" alt="image" src="https://github.com/user-attachments/assets/ae82d209-f9da-4f5c-b816-fd051e916448" />

# Executive Summary

## Overview of Findings

The bank demonstrated strong growth in customer activity between 1993 and 1998, surpassing 1 million total transactions and generating more than 103 million in total loan value, indicating increasing adoption of banking services and customer engagement over time. Despite this growth, approximately 11% of loans were identified as risky, with problematic loans concentrated in specific regions and among customers exhibiting unstable financial behavior.

Customer analytics further revealed that highly active customers and cardholders generally maintained stronger balances and greater engagement with the bank’s products, while risky customers were characterized by high monthly loan payments, withdrawal-heavy transaction patterns, and lower financial stability. 

Below is the overview page from the Power BI dashboard, and more examples are included throughout the report. The entire interactive dashboard can be downloaded here.

<img width="770" height="434" alt="image" src="https://github.com/user-attachments/assets/7cdcf8a8-f290-44e1-b32c-d3b17f4b6a50" />

## Transaction Trend:

- Transaction activity increased significantly between 1993 and 1998, rising from approximately 1M in early 1993 to peak levels above 200M by 1998. This consistent upward trend indicates rapid growth in customer engagement and banking service adoption over the analyzed period.

- The transaction trend demonstrates strong seasonal or cyclical spikes occurring almost every year, with notable peaks around 82M in 1995, 149M–181M in 1997, and over 210M in 1998. These recurring surges suggest periods of intensified banking activity, potentially driven by loan cycles, payment schedules, or increased customer usage.

- Although overall transaction volume continued to grow, the trend also exhibited several sharp short-term declines after major peaks. For example, transaction amounts dropped from approximately 210M to around 148M in 1998 after reaching the highest recorded peak, indicating volatility in customer transaction behavior and possible fluctuations in account activity.

- The long-term growth trajectory accelerated noticeably after 1996, where transaction values consistently exceeded 100M and continued climbing afterward. This suggests that the bank entered a stronger expansion phase during the later years, supported by increasing transaction frequency and higher overall financial activity across the customer base.

<img width="765" height="411" alt="image" src="https://github.com/user-attachments/assets/82b9d149-8947-4b2e-9fb4-3f77930408d7" />

## Customer Segmentation Scatter Plot

- Customers categorized as “Has Card” generated extremely high banking activity, contributing more than 1,056,320 total transactions. This suggests that card ownership is strongly associated with active engagement and frequent usage of banking services.

- Card-owning customers maintained an average account balance of approximately 38.5K, indicating relatively stable financial behavior and stronger liquidity compared to typical retail banking customers. The combination of high transaction activity and stable balances suggests these customers represent valuable long-term banking clients.

- The customer segment displayed substantial borrowing activity, with total loan amounts exceeding 103M. This indicates that highly engaged customers are also major users of the bank’s lending products, demonstrating opportunities for cross-selling and relationship banking strategies.

- The visualization currently shows a single dominant customer segment concentrated around high transaction counts, high balances, and high loan usage. This suggests either a highly homogeneous active customer base or an aggregation issue in the current dashboard design, indicating that deeper segmentation at the individual customer level may provide more actionable behavioral insights.

<img width="766" height="409" alt="image" src="https://github.com/user-attachments/assets/ea8e411f-34b7-4cd6-be25-baddfee546b8" />

## Loan Status by Region

- Across all regions, the majority of loans were categorized as “Running contract, OK so far” with approximately 403 loans per region belonging to this healthy loan segment. This indicates that most customers were actively repaying loans without major financial issues, suggesting an overall stable loan portfolio.

- Completed loans with no repayment problems represented the second-largest loan category, averaging around 203 loans across regions. This demonstrates that a significant portion of customers successfully fulfilled their loan obligations, reflecting relatively healthy long-term repayment behavior.

- Risk-related loan statuses, including “Running contract, client in debt” and “Contract finished, loan not payed” appeared consistently across nearly all regions. On average, each region contained approximately 45 active debt-related loans and 31 unpaid completed loans, indicating that loan risk is geographically widespread rather than isolated to a single district.

- While the overall loan status distribution remained relatively similar between regions, several districts such as central Bohemia, Prague, north Moravia, and south Bohemia showed slightly higher total loan counts, suggesting stronger banking activity and larger customer bases in these areas. This indicates that high-activity regions may require closer monitoring due to their larger exposure to both healthy and risky loans.

<img width="768" height="411" alt="image" src="https://github.com/user-attachments/assets/eff6abaf-ede8-4d5a-9689-28f118038486" />

## Monthly Payment and Loan Amount

- Loans categorized as “Running contract, OK so far” represented the largest loan segment and were associated with the highest financial exposure, reaching approximately 69M in total loan amount and over 1.5M in monthly payments. This indicates that the bank’s healthiest active loans also account for the largest share of the lending portfolio.

- Customers with “Contract finished, no problems” loans showed moderate loan sizes and repayment obligations, with loan amounts around 19M and monthly payments close to 0.9M. This suggests that stable repayment behavior is commonly associated with medium-sized loans and manageable payment structures.

- Riskier loan groups, particularly “Running contract, client in debt,” displayed relatively high loan amounts compared to their lower monthly payment volumes. With loan exposure exceeding 10M despite lower repayment capacity, these customers may represent financially stressed borrowers who require closer monitoring from the bank’s risk management team.

- The “Contract finished, loan not payed” segment represented the smallest portion of the portfolio, with both low loan amounts and low repayment values. Although smaller in scale, this category remains critical because it reflects fully defaulted loans that directly contribute to financial losses and deteriorating portfolio quality.

<img width="929" height="521" alt="image" src="https://github.com/user-attachments/assets/a2fbce7b-b837-4e29-805e-f6db95538e13" />

# Recommendations

Based on the insights and findings above, we would recommend the bank’s analytics, risk management, and customer strategy teams to consider the following:

- Customers with high loan amounts but relatively low repayment capacity should be monitored more proactively through early-warning risk systems. The analysis showed that debt-related loan groups maintained disproportionately high loan exposure despite lower monthly payment activity, indicating elevated financial stress and potential default risk.

- Regional loan monitoring strategies should be strengthened in high-activity districts such as central Bohemia, Prague, and north Moravia, where both healthy and risky loan volumes are significantly concentrated. Implementing region-specific risk policies may help reduce portfolio exposure while maintaining growth opportunities.
  
- The bank should expand engagement and retention programs targeting active card-owning customers. Dashboard findings revealed that card holders generated the highest transaction volumes, maintained stable balances, and represented some of the bank’s most valuable and engaged customers.

- Transaction behavior metrics such as withdrawal frequency, repayment burden, and balance stability should be incorporated into future credit scoring and loan approval models. The analysis demonstrated that risky customers often exhibit unstable financial behavior patterns before loan repayment issues occur.

- The bank should continue investing in customer acquisition and digital banking engagement initiatives, as transaction activity grew substantially between 1993 and 1998. Sustaining this growth while improving loan portfolio quality could significantly strengthen long-term customer profitability and financial stability.

## Loan 




