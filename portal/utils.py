from django.core.validators import RegexValidator


community_name_validator = RegexValidator(regex=r'^[A-Z0-9]+$',message="Community name must be in capital letters without any special characters.")

RELATIONSHIP_CHOICES = [
    ('Husband/Wife', 'Husband/Wife'),
    ('Son/Daughter', 'Son/Daughter'),
    ('Brother/Sister', 'Brother/Sister'),
    ('Son-in-law/Daughter-in-law', 'Son-in-law/Daughter-in-law'),
    ('Grandson/Granddaughter', 'Grandson/Granddaughter'),
    ('Niece/Nephew', 'Niece/Nephew'),
    ('Cousin', 'Cousin'),
    ("Worker's Family", "Worker's Family"),
    ('Worker', 'Worker'),
    ('Father/Mother', 'Father/Mother'),
    ('Other', 'Other (specify)')
]
# Gender of the household member
GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
]
# Nationality and country of origin
NATIONALITY_CHOICES = [
    ('Ghanaian', 'Ghanaian'),
    ('Non Ghanaian', 'Non Ghanaian'),
]
    # Country of origin if Non Ghanaian
COUNTRY_ORIGIN_CHOICES = [
    ('Burkina Faso', 'Burkina Faso'),
    ('Mali', 'Mali'),
    ('Guinea', 'Guinea'),
    ('Ivory Coast', 'Ivory Coast'),
    ('Liberia', 'Liberia'),
    ('Togo', 'Togo'),
    ('Benin', 'Benin'),
    ('Niger', 'Niger'),
    ('Nigeria', 'Nigeria'),
    ('Other', 'Other (specify)')
]
    # Whether the household member has a birth certificate
BIRTH_CERTIFICATE_CHOICES = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]
# Main work/occupation
MAIN_WORK_CHOICES = [
    ('Farmer_cocoa', 'Farmer (cocoa)'),
    ('Farmer_coffee', 'Farmer (coffee)'),
    ('Farmer_other', 'Farmer (other)'),
    ('Merchant', 'Merchant'),
    ('Student', 'Student'),
    ('Other', 'Other'),
    ('No_activity', 'No activity'),
]





GENDER_CHOICES = [
    ('Boy', 'Boy'),
    ('Girl', 'Girl'),
]
# Choices for birth certificate
BIRTH_CERTIFICATE_CHOICES = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]
    # Choices for Yes/No questions (you can adjust the codes if needed)
YES_NO_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
WHO_ANSWERS_CHOICES = [
    ('parents', 'The parents or legal guardians'),
    ('family_member', 'Another family member'),
    ('sibling', "One of the child's siblings"),
    ('other', 'Other'),
]
CHILD_UNAVAILABILITY_REASON_CHOICES = [
    ('school', 'The child is at school'),
    ('work_cocoa', 'The child has gone to work on the cocoa farm'),
    ('housework', 'Child is busy doing housework'),
    ('work_outside', 'Child works outside the household'),
    ('too_young', 'The child is too young'),
    ('sick', 'The child is sick'),
    ('travelled', 'The child has travelled'),
    ('play', 'The child has gone out to play'),
    ('sleeping', 'The child is sleeping'),
    ('other', 'Other reasons'),
]

FATHER_LOCATION_CHOICES = [
    ('same_household', 'In the same household'),
    ('another_household_village', 'In another household in the same village'),
    ('another_household_region', 'In another household in the same region'),
    ('another_household_other_region', 'In another household in another region'),
    ('abroad', 'Abroad'),
    ('parents_deceased', 'Parents deceased'),
    ('dont_know', "Don't know/Don't want to answer"),
]
COUNTRY_CHOICES = [
    ('Benin', 'Benin'), ('Burkina Faso', 'Burkina Faso'), ('Ghana', 'Ghana'),
    ('Guinea', 'Guinea'), ('Guinea-Bissau', 'Guinea-Bissau'), ('Liberia', 'Liberia'),
    ('Mauritania', 'Mauritania'), ('Mali', 'Mali'), ('Nigeria', 'Nigeria'),
    ('Niger', 'Niger'), ('Senegal', 'Senegal'), ('Sierra Leone', 'Sierra Leone'),
    ('Togo', 'Togo'), ('dont_know', "Don't know"), ('other', "Other"),
]


EDUCATION_STATUS_CHOICES = [(1, 'Yes'), (0, 'No')]
SCHOOL_TYPE_CHOICES = [('public', 'Public'), ('private', 'Private')]
GRADE_CHOICES = [
    ('K1', 'Kindergarten 1'), ('K2', 'Kindergarten 2'), ('P1', 'Primary 1'), ('P2', 'Primary 2'),
    ('P3', 'Primary 3'), ('P4', 'Primary 4'), ('P5', 'Primary 5'), ('P6', 'Primary 6'),
    ('JHS1', 'JHS/JSS 1'), ('JHS2', 'JHS/JSS 2'), ('JHS3', 'JHS/JSS 3'),
    ('SSS1', 'SSS/JHS 1'), ('SSS2', 'SSS/JHS 2'), ('SSS3', 'SSS/JHS 3'), ('SSS4', 'SSS/JHS 4'),
]
SCHOOL_GOING_TIMES_CHOICES = [('01', 'Once'), ('02', 'Twice'), ('03', 'Thrice'), ('04', 'Four times'), ('05', 'Five times')]
BASIC_NEED_CHOICES = [('books', 'Books'), ('bag', 'School bag'), ('pen', 'Pen / Pencils'), ('uniform', 'School Uniforms'), ('shoes', 'Shoes and Socks'), ('none', 'None of the above')]
SCHL2_CHOICES = [('01', 'Yes, they went to school but stopped'), ('00', 'No, they have never been to school')]


# --- Calculation Task ---
CALCULATION_RESPONSE_CHOICES = [
    ('both_correct', 'Yes, the child gave the right answer for both calculations'),
    ('one_correct', 'Yes, the child gave the right answer for one calculation'),
    ('wrong', 'No, the child does not know how to answer and gave wrong answers'),
    ('refused', 'The child refuses to try'),
]
# --- Reading Assessment ---
READING_RESPONSE_CHOICES = [
    ('can_read', 'Yes (he/she can read the sentences)'),
    ('simple_text', 'Only the simple text (text 1.)'),
    ('cannot_read', 'No'),
    ('refused', 'The child refuses to try'),
]
# --- Writing Assessment ---
WRITING_RESPONSE_CHOICES = [
    ('can_write_both', 'Yes, he/she can write both sentences'),
    ('simple_text', 'Only the simple text (text 1.)'),
    ('cannot_write', 'No'),
    ('refused', 'The child refuses to try'),
]
    # --- Education Level ---
EDUCATION_LEVEL_CHOICES = [
    ('pre_school', 'Pre-school (Kindergarten)'),
    ('primary', 'Primary'),
    ('jss', 'JSS/Middle school'),
    ('sss', "SSS/'O'-level/'A'-level (including vocational & technical training)"),
    ('university', 'University or higher'),
    ('not_applicable', 'Not applicable'),
]
# --- Reasons for Leaving School ---
SCHOOL_LEFT_REASON_CHOICES = [
    ('too_far', 'The school is too far away'),
    ('tuition', 'Tuition fees for private school too high'),
    ('poor_performance', 'Poor academic performance'),
    ('insecurity', 'Insecurity in the area'),
    ('learn_trade', 'To learn a trade'),
    ('early_pregnancy', 'Early pregnancy'),
    ('child_disinterest', 'The child did not want to go to school anymore'),
    ('affordability', "Parents can't afford Teaching and Learning Materials"),
    ('other', 'Other'),
    ('dont_know', "Does not know"),
]
# --- Reasons for Never Attending School ---
NEVER_SCHOOL_REASON_CHOICES = [
    ('too_far', 'The school is too far away'),
    ('tuition', 'Tuition fees too high'),
    ('too_young', 'Too young to be in school'),
    ('insecurity', 'Insecurity in the region'),
    ('learn_trade', 'To learn a trade (apprenticeship)'),
    ('child_disinterest', "The child doesn't want to go to school"),
    ('affordability', "Parents can't afford TLMs and/or enrollment fees"),
    ('other', 'Other'),
]
# --- School Attendance in the Past 7 Days ---
SCHOOL_7DAYS_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
SCHOOL_ABSENCE_REASON_CHOICES = [
    ('holidays', 'It was the holidays'),
    ('sick', 'He/she was sick'),
    ('working', 'He/she was working'),
    ('traveling', 'He/she was traveling'),
    ('other', 'Other'),
] 
    # Has the child missed school days in the past 7 days?
MISSED_SCHOOL_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
# If missed school, why did the child miss school?
MISSED_SCHOOL_REASON_CHOICES = [
    ('sick', 'He/she was sick'),
    ('working', 'He/she was working'),
    ('traveled', 'He/she traveled'),
    ('other', 'Other'),
]
# In the past 7 days, has the child worked in the house?
WORK_IN_HOUSE_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
    # In the past 7 days, has the child been working on the cocoa farm?
WORK_ON_COCOA_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
    # How often has the child worked in the past 7 days?
WORK_FREQUENCY_CHOICES = [
    ('every_day', 'Every day'),
    ('4-5_days', '4-5 days'),
    ('2-3_days', '2-3 days'),
    ('once', 'Once'),
]
    # Did the enumerator observe the child working in a real situation?
OBSERVED_WORK_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
    
TASK_CHOICES = [
    ('collect_fruits', 'Collect and gather fruits, pods, seeds after harvesting'),
    ('extract_cocoa', 'Extracting cocoa beans after shelling by an adult'),
    ('wash_items', 'Wash beans, fruits, vegetables or tubers'),
    ('prepare_germinators', 'Prepare the germinators and pour the seeds into the germinators'),
    ('collect_firewood', 'Collecting firewood'),
    ('measure_distance', 'To help measure distances between plants during transplanting'),
    ('sort_drying', 'Sort and spread the beans, cereals and other vegetables for drying'),
    ('put_cuttings', 'Putting cuttings on the mounds'),
    ('hold_bags', 'Holding bags or filling them with small containers for packaging de produits agricoles'),
    ('cover_products', 'Covering stored agricultural products with tarps'),
    ('shell_dehusk', 'To shell or dehusk seeds, plants and fruits by hand'),
    ('sowing', 'Sowing seeds'),
    ('transplant', 'Transplant or put in the ground the cuttings or plants'),
    ('harvest_legumes', 'Harvesting legumes, fruits and other leafy products (corn, beans, soybeans, various vegetables)'),
    ('none', 'None'),
]
REMUNERATION_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
] 
# 1. Longest time spent on light duty during a SCHOOL DAY in the last 7 days
LIGHT_DUTY_DURATION_CHOICES = [
    ('<1', 'Less than 1 hour'),
    ('1-2', '1-2 hour'),
    ('2-3', '2-3 hours'),
    ('3-4', '3-4 hours'),
    ('4-6', '4-6 hours'),
    ('6-8', '6-8 hours'),
    ('>8', 'More than 8 hours'),
    ('na', 'Does not apply'),
]
    
# 2. Longest time spent on light duty during a NON-SCHOOL DAY in the last 7 days
LIGHT_DUTY_DURATION_NON_SCHOOL_CHOICES = [
    ('<1', 'Less than 1 hour'),
    ('1-2', '1-2 hour'),
    ('2-3', '2-3 hours'),
    ('3-4', '3-4 hours'),
    ('4-6', '4-6 hours'),
    ('6-8', '6-8 hours'),
    ('>8', 'More than 8 hours'),
]
    # 3. Where was this task done?
TASK_LOCATION_CHOICES = [
    ('family_farm', 'On family farm'),
    ('hired_labour', 'As a hired labourer on another farm'),
    ('school_farms', 'School farms/compounds'),
    ('teachers_farms', 'Teachers farms (during communal labour)'),
    ('church_farms', 'Church farms or cleaning activities'),
    ('community_help', 'Helping a community member for free'),
    ('other', 'Other'),
]
# 6. Was the child under supervision of an adult when performing this task?
SUPERVISION_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
TASK_CHOICES_12MONTHS = [
    ('collect_fruits', 'Collect and gather fruits, pods, seeds after harvesting'),
    ('extract_cocoa', 'Extracting cocoa beans after shelling by an adult'),
    ('wash_items', 'Wash beans, fruits, vegetables or tubers'),
    ('prepare_germinators', 'Prepare the germinators and pour the seeds into the germinators'),
    ('collect_firewood', 'Collecting firewood'),
    ('measure_distance', 'To help measure distances between plants during transplanting'),
    ('sort_drying', 'Sort and spread the beans, cereals and other vegetables for drying'),
    ('put_cuttings', 'Putting cuttings on the mounds'),
    ('hold_bags', 'Holding bags or filling them with small containers for packaging de produits agricoles'),
    ('cover_products', 'Covering stored agricultural products with tarps'),
    ('shell_dehusk', 'To shell or dehusk seeds, plants and fruits by hand'),
    ('sowing', 'Sowing seeds'),
    ('transplant', 'Transplant or put in the ground the cuttings or plants'),
    ('harvest_legumes', 'Harvesting legumes, fruits and other leafy products (corn, beans, soybeans, various vegetables)'),
    ('none', 'None'),
]
# Remuneration received for the activity.
REMUNERATION_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
# 1. Longest time spent on light duty during a SCHOOL DAY in the last 7 days
LIGHT_DUTY_DURATION_SCHOOL_CHOICES = [
    ('<1', 'Less than 1 hour'),
    ('1-2', '1-2 hour'),
    ('2-3', '2-3 hours'),
    ('3-4', '3-4 hours'),
    ('4-6', '4-6 hours'),
    ('6-8', '6-8 hours'),
    ('>8', 'More than 8 hours'),
    ('na', 'Does not apply'),
]
# 2. Longest time spent on light duty during a NON-SCHOOL DAY in the last 7 days
LIGHT_DUTY_DURATION_NON_SCHOOL_CHOICES = [
    ('<1', 'Less than 1 hour'),
    ('1-2', '1-2 hour'),
    ('2-3', '2-3 hours'),
    ('3-4', '3-4 hours'),
    ('4-6', '4-6 hours'),
    ('6-8', '6-8 hours'),
    ('>8', 'More than 8 hours'),
]
# 3. Where was this task done?
TASK_LOCATION_CHOICES = [
    ('family_farm', 'On family farm'),
    ('hired_labour', 'As a hired labourer on another farm'),
    ('school_farms', 'School farms/compounds'),
    ('teachers_farms', 'Teachers farms (during communal labour)'),
    ('church_farms', 'Church farms or cleaning activities'),
    ('community_help', 'Helping a community member for free'),
    ('other', 'Other'),
]
# 6. Was the child under supervision of an adult when performing this task?
SUPERVISION_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
    # --- Heavy Tasks on Cocoa Farm in the Last 7 Days ---
HEAVY_TASK_CHOICES = [
    ('machetes_weeding', 'Use of machetes for weeding or pruning (Clearing)'),
    ('felling_trees', 'Felling of trees'),
    ('burning_plots', 'Burning of plots'),
    ('game_hunting', 'Game hunting with a weapon'),
    ('woodcutter_work', "Woodcutter's work"),
    ('charcoal_production', 'Charcoal production'),
    ('stump_removal', 'Stump removal'),
    ('digging_holes', 'Digging holes'),
    ('sharp_tool_work', 'Working with a machete or any other sharp tool'),
    ('handling_agrochemicals', 'Handling of agrochemicals'),
    ('driving_vehicles', 'Driving motorized vehicles'),
    ('carrying_heavy_loads', 'Carrying heavy loads (Boys: 14-16 years old >15kg / 16-17 years old >20kg; Girls: 14-16 years old >8Kg / 16-17 years old >10Kg)'),
    ('night_work', 'Night work on farm (between 6pm and 6am)'),
    ('none', 'None of the above'),
]
# --- Salary ---
SALARY_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
    # --- Task Location ---
TASK_LOCATION_CHOICES = [
    ('family_farm', 'On family farm'),
    ('hired_labour', 'As a hired labourer on another farm'),
    ('school_farms', 'School farms/compounds'),
    ('teachers_farms', 'Teachers farms (during communal labour)'),
    ('church_farms', 'Church farms or cleaning activities'),
    ('community_help', 'Helping a community member for free'),
    ('other', 'Other'),
]
DURATION_CHOICES_SCHOOL = [
    ('less_than_1', 'Less than one hour'),
    ('1_hour', '1 hour'),
    ('2_hours', '2 hours'),
    ('3-4_hours', '3-4 hours'),
    ('4-6_hours', '4-6 hours'),
    ('6-8_hours', '6-8 hours'),
    ('more_than_8', 'More than 8 hours'),
    ('does_not_apply', 'Does not apply'),
]
# Longest time spent on the task during a NON-SCHOOL DAY in the last 7 days
DURATION_CHOICES_NON_SCHOOL = [
    ('less_than_1', 'Less than one hour'),
    ('1-2_hours', '1-2 hour'),
    ('2-3_hours', '2-3 hours'),
    ('3-4_hours', '3-4 hours'),
    ('4-6_hours', '4-6 hours'),
    ('6-8_hours', '6-8 hours'),
    ('more_than_8', 'More than 8 hours'),
]
# --- Supervision ---
SUPERVISION_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]

# Tasks performed in the last 12 months on the cocoa farm.
HEAVY_TASK_CHOICES_12MONTHS = [
    ('machetes_weeding', 'Use of machetes for weeding or pruning (Clearing)'),
    ('felling_trees', 'Felling of trees'),
    ('burning_plots', 'Burning of plots'),
    ('game_hunting', 'Game hunting with a weapon'),
    ('woodcutter_work', "Woodcutter's work"),
    ('charcoal_production', 'Charcoal production'),
    ('stump_removal', 'Stump removal'),
    ('digging_holes', 'Digging holes'),
    ('sharp_tool_work', 'Working with a machete or any other sharp tool'),
    ('handling_agrochemicals', 'Handling of agrochemicals'),
    ('driving_vehicles', 'Driving motorized vehicles'),
    ('carrying_heavy_loads', 'Carrying heavy loads (Boys: 14-16 years old >15kg / 16-17 years old >20kg; Girls: 14-16 years old >8Kg / 16-17 years old >10Kg)'),
    ('night_work', 'Night work on farm (between 6pm and 6am)'),
    ('none', 'None of the above'),
]
    
# Where the task was performed.
TASK_LOCATION_CHOICES = [
    ('family_farm', 'On family farm'),
    ('hired_labour', 'As a hired labourer on another farm'),
    ('school_farms', 'School farms/compounds'),
    ('teachers_farms', 'Teachers farms (during communal labour)'),
    ('church_farms', 'Church farms or cleaning activities'),
    ('community_help', 'Helping a community member for free'),
    ('other', 'Other'),
]
YES_NO_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
# --- Heavy Work Duration (Last 7 Days) ---
LONGEST_TIME_SCHOOL_DAY_CHOICES = [
    ('<1', 'Less than one hour'),
    ('1', '1 hour'),
    ('2', '2 hours'),
    ('3-4', '3-4 hours'),
    ('4-6', '4-6 hours'),
    ('6-8', '6-8 hours'),
    ('>8', 'More than 8 hours'),
    ('na', 'Does not apply'),
]
LONGEST_TIME_NON_SCHOOL_DAY_CHOICES = [
    ('<1', 'Less than one hour'),
    ('1-2', '1-2 hour'),
    ('2-3', '2-3 hours'),
    ('3-4', '3-4 hours'),
    ('4-6', '4-6 hours'),
    ('6-8', '6-8 hours'),
    ('>8', 'More than 8 hours'),
]
    # --- Work Details ---
WORK_FOR_WHOM_CHOICES = [
    ('parents', "For his/her parents"),
    ('family_not_parents', "For family, not parents"),
    ('family_friends', "For family friends"),
    ('other', "Other"),
]
WORK_REASON_CHOICES = [
    ('own_money', "To have his/her own money"),
    ('increase_income', "To increase household income"),
    ('cannot_afford_adult', "Household cannot afford adult's work"),
    ('cannot_find_adult', "Household cannot find adult labor"),
    ('learn_cocoa', "To learn cocoa farming"),
    ('other', "Other"),
    ('does_not_know', "Does not know"),
]
INJURY_CAUSE_CHOICES = [
    ('playing_outside', "Playing outside"),
    ('household_chores', "Doing household chores"),
    ('helping_farm', "Helping on the farm"),
    ('falling_bicycle', "Falling of a bicycle, scooters or tricycle"),
    ('animal_insect', "Animal or insect bite or scratch"),
    ('fighting', "Fighting with someone else"),
    ('other', "Other"),
]
WOUND_TIME_CHOICES = [
    ('<week', "Less than a week ago"),
    ('1week-1month', "More than one week and less than a month"),
    ('2-6months', "More than 2 months and less than 6 months"),
    ('>6months', "More than 6 months"),
]
HELP_CHILD_HEALTH_CHOICES = [
    ('household_adults', "The adults of the household looked after him/her"),
    ('community_adults', "Adults of the community looked after him/her"),
    ('medical_facility', "The child was sent to the closest medical facility"),
    ('no_help', "The child did not receive any help"),
    ('other', "Other"),
]


capital_letters_numbers_validator = RegexValidator(regex=r'^[A-Z0-9\s]+$', message="Only capital letters, numbers, and spaces are allowed.")

CHILD_BORN_CHOICES = [('Yes', 'Yes'), ('DiffComm', 'No, born in this district but different community'), ('DiffDist', 'No, born in this region but different district'), ('DiffReg', 'No, born in another region of Ghana'), ('AnotherCountry', 'No, born in another country')]
COUNTRY_OF_BIRTH_CHOICES = [('Benin', 'Benin'), ('BurkinaFaso', 'Burkina Faso'), ('IvoryCoast', 'Ivory Coast'), ('Mali', 'Mali'), ('Niger', 'Niger'), ('Togo', 'Togo'), ('Other', 'Other')]
CHILD_RELATIONSHIP_CHOICES = [('Son/Daughter', 'Son/Daughter'), ('Brother/Sister', 'Brother/Sister'), ('SonInLaw/DaughterInLaw', 'Son-in-law/Daughter-in-law'), ('Grandson/Granddaughter', 'Grandson/Granddaughter'), ('Niece/Nephew', 'Niece/nephew'), ('Cousin', 'Cousin'), ('ChildOfWorker', "Child of the worker"), ('ChildOfOwner', "Child of the farm owner"), ('Other', 'Other')]
CHILD_NOT_LIVE_REASONS = [('ParentsDeceased', 'Parents deceased'), ('CantCare', "Can't take care of me"), ('Abandoned', 'Abandoned'), ('SchoolReasons', 'School reasons'), ('AgencyBrought', 'A recruitment agency brought me here'), ('DidNotWant', 'I did not want to live with my parents'), ('Other', 'Other')]
CHILD_DECISION_MAKER_CHOICES = [('Myself', 'Myself'), ('Parents', 'Father/Mother'), ('Grandparents', 'Grandparents'), ('OtherFamily', 'Other family members'), ('External', 'External recruiter/agency'), ('Other', 'Other person')]
YES_NO_CHOICES = [('Yes', 'Yes'), ('No', 'No')]
LAST_SEEN_CHOICES = [('1week', 'Max 1 week'), ('1month', 'Max 1 month'), ('1year', 'Max 1 year'), ('MoreThan1year', 'More than 1 year'), ('Never', 'Never')]
LIVING_DURATION_CHOICES = [('Born', 'Born in the household'), ('Less1', 'Less than 1 year'), ('1-2', '1-2 years'), ('2-4', '2-4 years'), ('4-6', '4-6 years'), ('6-8', '6-8 years'), ('More8', 'More than 8 years'), ('DontKnow', "Don't know")]
CHILD_ACCOMPANIED_CHOICES = [('Alone', 'Came alone'), ('Parents', 'Father/Mother'), ('Grandparents', 'Grandparents'), ('OtherFamily', 'Other family member'), ('WithRecruit', 'With a recruit'), ('Other', 'Other')]


AGREE_OR_DISAGREE = [
    ('Agree', 'Agree'),
    ('Disagree', 'Disagree'),
]
# For the worker agreement type, we allow an "Other" option requiring specification.
WORKER_AGREEMENT_CHOICES = [
    ('VerbalWithoutWitness', 'Verbal agreement without witness'),
    ('VerbalWithWitness', 'Verbal agreement with witness'),
    ('WrittenWithoutWitness', 'Written agreement without witness'),
    ('WrittenWithWitness', 'Written contract with witness'),
    ('Other', 'Other'),
]
# For the type of worker recruitment.
WORKER_RECRUITMENT_CHOICES = [
    ('Permanent', 'Permanent labor'),
    ('Casual', 'Casual labor'),
]
# For salary status.
SALARY_STATUS_CHOICES = [
    ('Always', 'Always'),
    ('Sometimes', 'Sometimes'),
    ('Rarely', 'Rarely'),
    ('Never', 'Never'),
]
REFUSAL_ACTION_CHOICES = [
        ('Compromise', 'I find a compromise'),
        ('SalaryDeduction', 'I withdraw part of their salary'),
        ('Warning', 'I issue a warning'),
        ('Other', 'Other'),
        ('NotApplicable', 'Not applicable'),
    ]

YES_OR_NO = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]



COMMUNITY_CHOICES = [
    ('Town', 'Town'),
    ('Village', 'Village'),
    ('Camp', 'Camp'),
]
YES_OR_NO = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]
UNAVAILABLE_REASON_CHOICES = [
    ('Non-resident', 'Non-resident'),
    ('Deceased', 'Deceased'),
    ("Doesn't work with TOUTON anymore", "Doesn't work with TOUTON anymore"),
    ('Other', 'Other'),
]
ANSWER_BY_CHOICES = [
    ('Caretaker', 'Caretaker'),
    ('Spouse', 'Spouse'),
    ('Nobody', 'Nobody'),
]



CORRECT_RESPONSE_PROVIDED = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]
NATIONALITY_CHOICES = [
    ('Ghanaian', 'Ghanaian'),
    ('Non Ghanaian', 'Non Ghanaian'),
]
COUNTRY_ORIGIN_CHOICES = [
    ('Burkina Faso', 'Burkina Faso'),
    ('Mali', 'Mali'),
    ('Guinea', 'Guinea'),
    ('Ivory Coast', 'Ivory Coast'),
    ('Liberia', 'Liberia'),
    ('Togo', 'Togo'),
    ('Benin', 'Benin'),
    ('Niger', 'Niger'),
    ('Nigeria', 'Nigeria'),
    ('Other', 'Other'),
]
CORRECT_RESPONSE_PROVIDED = [
    ('Yes', 'Yes'),
    ('No', 'No'),
]
OWNER_STATUS_CHOICES = [
    ('Complete Owner', 'Complete Owner'),
    ('Sharecropper', 'Sharecropper'),
    ('Owner/Sharecropper', 'Owner/Sharecropper'),
]
OWNER_STATUS_CHOICES = [
    ('Coaretaker/Manager of the farm', 'Coaretaker/Manager of the farm'),
    ('Sharecropper', 'Sharecropper'),
]
    # Nationality of the owner
NATIONALITY_OWNER_CHOICES = [
    ('Ghanaian', 'Ghanaian'),
    ('Non Ghanaian', 'Non Ghanaian'),
]
    # Country of origin of the owner (if Non Ghanaian)
COUNTRY_ORIGIN_OWNER_CHOICES = [
    ('Burkina Faso', 'Burkina Faso'),
    ('Mali', 'Mali'),
    ('Guinea', 'Guinea'),
    ('Ivory Coast', 'Ivory Coast'),
    ('Liberia', 'Liberia'),
    ('Togo', 'Togo'),
    ('Benin', 'Benin'),
    ('Other', 'Other'),
]


YES_OR_NO = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]



SCHOOL_FEES_CHOICES = [
    ('yes', 'Yes'),
    ('no', 'No'),
]
    # Question 2: What should be done for the parent to stop involving their children in child labour?
PARENT_REMEDIATION_CHOICES = [
    ('child_protection', 'Child protection and parenting education'),
    ('school_kits', 'School kits support'),
    ('iga_support', 'IGA support'),
    ('other', 'Other'),
]
COMMUNITY_REMEDIATION_CHOICES = [
    ('community_education', 'Community education on child labour'),
    ('school_building', 'Community school building'),
    ('school_renovation', 'Community school renovation'),
    ('other', 'Other'),
]