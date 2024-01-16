# AWS pricing
## Introduction
One of the main reasons for moving to the cloud is cost. If done well, public cloud infrastructures can reduce costs significantly compared to traditional data centers. This is done by adopting a pay-as-you-go pricing model and economies of scale.

You pay only for the compute capacity, storage, and outbound data transfer that you use. You never pay for inbound data transfer and data transfer between services within the same region.

AWS lists four advantages of their pricing model:

- Pay-as-you-go
- Save when you commit
- Pay less by using more
- Benefit from massive economies of scale

The AWS Free Tier is a program that offers new AWS users free access to certain AWS services for a limited time (12 months from the date of sign-up) and provides a set of Always Free services that do not expire.

**CapEx (Capital Expenditure):**
- Involves long-term investments in assets.
- Costs are spread over time through depreciation or amortization.
- Impacts the balance sheet, contributing to the overall value of the business.

*Examples include the purchase of buildings, machinery, or development of new technology.*

**OpEx (Operational Expenditure):**
- Represents day-to-day operational costs.
- Costs are fully expensed in the period they occur.
- Directly impacts the income statement, influencing profitability.

*Examples include salaries, rent, utilities, and marketing expenses.*

## Exercise
`1. Create an alert that you can use to monitor your own cloud costs.`

I did so by following these steps:
1. Log in to the AWS Management Console.
2. Go to the AWS Budgets section.
3. Click on "Create budget."
4. Select the type of budget you want to create such as a Cost budget.
5. Provide the details for your budget, including its name, duration and the amount you want to allocate.
6. Define thresholds for alerts. Specify who should receive them.
7. Save your budget setup.

![PrnScr](/00_includes/04_AWS1/1_budget_alert.png)



This means I will be notified via email when any spend above 25%, 50% and 75% of the total balance (50 euro) is incurred. This allows me to keep track of my budget.

`2. Understand the options that AWS offers to get insights in your cloud costs. `

AWS offers several tools and services to help users gain insights into their cloud costs, monitor usage and optimize spending. AWS Budget is an example of this.

## Sources
- https://www.youtube.com/watch?v=O0sofGVT7uw

- https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-create.html#create-cost-budget