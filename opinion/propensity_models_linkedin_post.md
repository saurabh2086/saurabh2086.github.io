The most common, expensive mistake ML teams make in banking is confusing **propensity** with **uplift**. 

Here is a simple thought experiment I run when auditing data science teams:

Suppose you are running marketing for a retail bank. Your business goal is to maximize attendance at an upcoming investment seminar. 

To help boost attendance, the business hands you a budget of **100 taxi vouchers** to distribute to customers. 

You build a highly accurate, state-of-the-art propensity model to predict which customers are most likely to show up. 

What should you do with the 100 vouchers? 

If you do what 90% of ML teams do, you rank customers by their propensity scores and send the vouchers to the top 100. 

Sounds logical, right? 

**Wrong. It is a complete waste of budget.**

Think about it: the customers with the highest propensity scores are the ones *already* most likely to attend. They are your brand advocates, your highly active investors, or customers who live next door. 

If you send them a voucher, they will use it and attend. But they would have attended anyway without it. 

You haven't changed their behavior; you have just paid for a ride they were already going to take.

To solve this, we have to look at the problem through the lens of **Causal Inference and Uplift Modeling**. We need to divide our customer base into four distinct buckets:

1. **The Sure Things**: They will attend regardless of whether they receive a voucher. (High propensity, zero treatment effect. *Do not waste vouchers here.*)
2. **The Lost Causes**: They will not attend, even if you offer them a free helicopter ride. (Low propensity, zero treatment effect. *Do not waste vouchers here.*)
3. **The Sleeping Dogs**: They were planning to attend, but sending them an email with a voucher triggers them to look at their calendar, realize they are busy, and cancel. (Or in credit card churn: prompting them with a retention offer reminds them they want to close the card). *Do not wake them up.*
4. **The Persuadables**: They want to attend, but the friction of travel is holding them back. If you send them a voucher, they show up. If you don't, they stay home. (Moderate propensity, **high treatment effect**.)

To maximize your seminar's strength, your 100 vouchers must go **exclusively to the Persuadables**. 

The goal of data science in business is rarely to predict what *will* happen. The goal is to predict how our *interventions* will change what happens. 

If your model is only predicting the baseline probability of an event, you aren't optimizing marketing. You are just subsidizing your most loyal customers.

Have you seen propensity models used this way in your teams? 

#DataScience #MachineLearning #CausalInference #MarketingAnalytics #Banking
