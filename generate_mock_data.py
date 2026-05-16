import os

os.makedirs('data/contracts', exist_ok=True)
os.makedirs('data/case_law', exist_ok=True)

contracts = {
    "supply_agreement_alpha_beta.txt": """SUPPLY AGREEMENT

This Supply Agreement is made between Alpha Corp ("Buyer") and BetaSupply ("Supplier"), signed in 2018.

Term: 3 years.
Obligations: BetaSupply shall deliver components according to the schedule.

Force Majeure Clause:
Neither party shall be liable for any failure or delay in performance under this Agreement due to causes beyond its reasonable control, including but not limited to natural disasters, acts of God, and governmental action. This clause does not cover pandemics or widespread disease.
""",
    "employment_agreement_california_engineer.txt": """EMPLOYMENT AGREEMENT

Employee: Software Engineer
Location: California

Non-Compete Clause:
During the term of this Agreement and for a period of two (2) years thereafter, the Employee agrees not to engage in or work for any competitor in the SaaS industry anywhere within the United States.

Choice of Law:
This Agreement shall be governed by and construed in accordance with the laws of the State of Texas, without giving effect to any choice of law principles.
""",
    "data_processing_agreement_cloud_vendor.txt": """DATA PROCESSING AGREEMENT

Parties: European Fintech Company (Controller) and Cloud Vendor (Processor)

Security Measures:
The Processor agrees to implement industry-standard security measures to protect Personal Data. However, specific encryption requirements are not mandated under this section.
Liability Cap:
The total liability of the Processor for any breach of this DPA shall not exceed $1,000,000.
""",
    "employment_agreement_data_scientist.txt": """EMPLOYMENT AGREEMENT

Employee: Data Scientist

Intellectual Property Assignment Clause:
The Employee agrees that all inventions, discoveries, designs, algorithms, and ideas conceived or reduced to practice during the term of employment are the sole and exclusive property of the Employer, regardless of whether such inventions were conceived during business hours or using Employer resources.
""",
    "logistics_contract_ecommerce.txt": """LOGISTICS AGREEMENT

Parties: E-commerce Platform and Logistics Company

Scope: Deliver 10,000 packages during peak holiday season.

Liquidated Damages:
In the event of delayed delivery, the Logistics Company shall pay liquidated damages of $50 per package per day of delay.
""",
    "saas_enterprise_subscription.txt": """ENTERPRISE SAAS SUBSCRIPTION AGREEMENT

Section 12.4: Auto-Renewal
This Agreement shall automatically renew for successive one-year terms at the then-current annual rate of $120,000, unless either party provides written notice of cancellation at least ninety (90) days prior to the end of the current term.

Signatures: Electronically signed by both parties.
""",
    "construction_contract_fixed_price.txt": """FIXED-PRICE CONSTRUCTION CONTRACT

Parties: General Contractor and Commercial Office Owner
Value: $5,000,000

Change Orders:
Any modification or addition to the scope of work must be documented in a written Change Order signed by both the Owner and the Contractor before work commences.
""",
    "nda_vp_sales.txt": """NON-DISCLOSURE AGREEMENT

Employee: VP of Sales

Confidentiality Clause:
The Employee agrees not to disclose or use any Confidential Information, including customer lists, pricing structures, deal pipelines, and trade secrets, for the benefit of any third party or competitor after the termination of employment.
""",
    "terms_of_service_consumer.txt": """ONLINE TERMS OF SERVICE

Arbitration Clause and Class Action Waiver:
Any dispute arising out of or related to these Terms shall be resolved exclusively through mandatory individual arbitration. The User waives any right to participate in a class action lawsuit or class-wide arbitration. Arbitration costs shall be borne by the User.
"""
}

case_law = {
    "california_bus_prof_code_16600.txt": """California Business and Professions Code Section 16600

Except as provided in this chapter, every contract by which anyone is restrained from engaging in a lawful profession, trade, or business of any kind is to that extent void.
Precedent: California courts strictly interpret Section 16600 to invalidate employee non-compete agreements unless a specific statutory exception applies.
""",
    "california_labor_code_2870.txt": """California Labor Code Section 2870

(a) Any provision in an employment agreement which provides that an employee shall assign, or offer to assign, any of his or her rights in an invention to his or her employer shall not apply to an invention that the employee developed entirely on his or her own time without using the employer's equipment, supplies, facilities, or trade secret information.
""",
    "gdpr_article_32_83.txt": """General Data Protection Regulation (GDPR)

Article 32: Security of Processing
Taking into account the state of the art, the costs of implementation and the nature, scope, context and purposes of processing, the controller and the processor shall implement appropriate technical and organisational measures to ensure a level of security appropriate to the risk, including inter alia as appropriate: the pseudonymisation and encryption of personal data.

Article 83: General conditions for imposing administrative fines
Infringements of the basic principles for processing, including conditions for consent, are subject to administrative fines up to 20,000,000 EUR, or in the case of an undertaking, up to 4 % of the total worldwide annual turnover of the preceding financial year, whichever is higher.
""",
    "liquidated_damages_precedent.txt": """Liquidated Damages vs Penalty Precedents

US Courts: A liquidated damages clause is enforceable if it is a genuine pre-estimate of loss at the time of contracting and actual damages are difficult to ascertain. If the amount is disproportionate to the expected loss, it is deemed an unenforceable penalty.
English Courts (Cavendish Square): The test is whether the provision is a secondary obligation which imposes a detriment out of all proportion to any legitimate interest of the innocent party.
""",
    "whistleblower_protections.txt": """Whistleblower Protections

Sarbanes-Oxley Act (SOX): Protects employees of publicly traded companies who report fraudulent activities.
Dodd-Frank Act: Provides financial incentives and anti-retaliation protections for whistleblowers reporting securities law violations.
At-Will Employment Exceptions: Many states recognize a public policy exception to at-will employment, preventing employers from terminating employees for refusing to commit an illegal act or reporting legal violations.
""",
    "dtsa_trade_secrets.txt": """Defend Trade Secrets Act (DTSA)

Under the DTSA, a trade secret includes financial, business, scientific, technical, economic, or engineering information if the owner has taken reasonable measures to keep such information secret and the information derives independent economic value from not being generally known. Customer lists can qualify as trade secrets if these conditions are met. Injunctive relief and damages are available remedies.
""",
    "att_mobility_v_concepcion.txt": """AT&T Mobility LLC v. Concepcion

The Supreme Court held that the Federal Arbitration Act (FAA) preempts state laws that prohibit contracts from disallowing class-action arbitration. Thus, class-action waivers in consumer arbitration agreements are generally enforceable.
"""
}

for filename, content in contracts.items():
    with open(f"data/contracts/{filename}", 'w') as f:
        f.write(content)

for filename, content in case_law.items():
    with open(f"data/case_law/{filename}", 'w') as f:
        f.write(content)

print("Mock data generated successfully.")
