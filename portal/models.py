from decimal import Decimal
from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.forms import ValidationError
from multiselectfield import MultiSelectField
from datetime import datetime
from django.contrib.auth import get_user_model
from .utils import *
#group
from django.contrib.auth.models import Group
#timezone
from django.utils import timezone

User = get_user_model()

# Validators
letters_only_validator = RegexValidator(regex=r'^[A-Za-z]+$',message='This field must contain only letters (no spaces).')
words_validator = RegexValidator(regex=r'^[A-Za-z\s]+$',message='This field must contain only letters and spaces.')
allowed_chars_validator = RegexValidator(regex=r'^[0-9A-Za-z\'\s]+$',message="Only numbers, letters, spaces and apostrophes are allowed. Accents are not allowed.")
name_validator = RegexValidator( regex=r'^[0-9A-Za-z\s\']+$',message="Only letters, numbers, spaces, and apostrophes are allowed. Accents are not allowed.")

class protectedValueError(Exception):
    def __init__(self, msg):
        super(protectedValueError, self).__init__(msg)

# Fix the base model classes
class timeStampQuerySet(models.QuerySet):
    def delete(self):
        for item in self:
            item.delete()
        return super(timeStampQuerySet, self)

    def hard_delete(self):
        return super(timeStampQuerySet, self).delete()

    def alive(self):
        return self.filter(delete_field="no")

    def dead(self):
        return self.filter(delete_field="yes")

class timeStampManager(models.Manager):
    def __init__(self, *args, **kwargs):
        self.alive_only = kwargs.pop('alive_only', True)
        super(timeStampManager, self).__init__(*args, **kwargs)

    def get_queryset(self):
        if self.alive_only:
            return timeStampQuerySet(self.model).filter(delete_field="no")
        return timeStampQuerySet(self.model)

    def hard_delete(self):
        return self.get_queryset().hard_delete()

class timeStamp(models.Model):  # Changed to inherit from models.Model
    """
    Description: This models is an abstract class that defines the columns that should be present in every table.
    """
    created_date = models.DateTimeField(auto_now=True)
    delete_field = models.CharField(max_length=10, default="no")
    
    objects = timeStampManager()
    default_objects = models.Manager()
    
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.delete_field = "yes"
        self.save()

class regionTbl(timeStamp):
    region = models.CharField(max_length=250, blank=True, null=True)
    
    def __str__(self):
        return str(self.region)
    
    class Meta:
        verbose_name_plural = "Region"


class districtTbl(timeStamp):
        regionTbl_foreignkey = models.ForeignKey('regionTbl',on_delete=models.CASCADE,blank=True, null=True)
        district        = models.CharField(max_length=250,blank=True, null=True)
        district_code   = models.CharField(max_length=250,blank=True, null=True,unique=True)
        def __str__(self):
                return str(self.district)
        class Meta:
                verbose_name_plural = "District"


class staffTbl(timeStamp):
    """
    Description: Contains details for Staff, Facilitators and other key personnel
    """

    GENDER_CHOICES = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    gender = models.CharField(max_length=250, choices=GENDER_CHOICES)
    contact = models.CharField(max_length=250)
    designation = models.ForeignKey(Group, on_delete=models.CASCADE)
    email_address = models.EmailField(max_length=250, blank=True)
    uid = models.CharField(max_length=2500, blank=True, null=True)
    fbase_code = models.CharField(max_length=2500, blank=True, null=True)
    district = models.CharField(max_length=250, blank=True, null=True)
    staffid = models.CharField(max_length=250, blank=True, null=True, unique=True)
    cmpassword = models.CharField(max_length=250, default="P@ssw0rd24")

    def __str__(self):
        return str(f'{self.first_name} {self.last_name}')
    
    class Meta:
        verbose_name_plural = "Staff Details"

    def save(self, *args, **kwargs):
        if not self.staffid:
            # Generate staff ID only if it doesn't exist
            self.staffid = self.generate_staff_id()
        super().save(*args, **kwargs)

    def generate_staff_id(self):
        """
        Generate staff ID in format CJCL-CRAXXX starting from 069
        """
        # Get the last staff ID
        last_staff = staffTbl.objects.filter(staffid__isnull=False).order_by('-staffid').first()
        
        if last_staff and last_staff.staffid:
            try:
                # Extract the numeric part from the last staff ID
                last_number = int(last_staff.staffid.split('-')[-1][3:])
                next_number = last_number + 1
            except (ValueError, IndexError):
                # If parsing fails, start from 069
                next_number = 69
        else:
            # If no staff exists yet, start from 069
            next_number = 69
        
        # Format the number with leading zeros (3 digits)
        number_str = str(next_number).zfill(3)
        return f"CJCL-CRA{number_str}"






# models.py - Add these models to your existing models

class PriorityLevel(timeStamp):
    """
    Description: Priority levels for deadlines (e.g., High, Medium, Low)
    """
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color code
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Priority Levels"


class DeadlineType(timeStamp):
    """
    Description: Types of deadlines (e.g., Data Collection, Reporting, Training)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Deadline Types"


class DeadlineAssignment(timeStamp):
    """
    Description: Assign deadlines and priorities to staff/enumerators
    """
    STAFF_TYPE_CHOICES = (
        ('Staff', 'Staff'),
        ('Enumerator', 'Enumerator'),
    )
    
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Overdue', 'Overdue'),
    )
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deadline_type = models.ForeignKey(DeadlineType, on_delete=models.CASCADE)
    priority_level = models.ForeignKey(PriorityLevel, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(staffTbl, on_delete=models.CASCADE, related_name='deadline_assignments')
    assigned_by = models.ForeignKey(staffTbl, on_delete=models.CASCADE, related_name='assigned_deadlines')
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPE_CHOICES, default='Staff')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    completion_date = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=100, blank=True, null=True)  # e.g., "weekly", "monthly"
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to}"
    
    def save(self, *args, **kwargs):
        # Update status based on dates
        now = timezone.now()
        if self.completion_date:
            self.status = 'Completed'
        elif self.end_date < now and self.status != 'Completed':
            self.status = 'Overdue'
        elif self.start_date <= now <= self.end_date and self.status == 'Pending':
            self.status = 'In Progress'
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        return self.status == 'Overdue'
    
    @property
    def days_remaining(self):
        if self.status == 'Completed':
            return 0
        remaining = (self.end_date - timezone.now()).days
        return max(0, remaining) if remaining > 0 else abs(remaining)
    
    class Meta:
        verbose_name_plural = "Deadline Assignments"
        ordering = ['-created_date']







class societyTbl(timeStamp):
        districtTbl_foreignkey = models.ForeignKey('districtTbl',on_delete=models.CASCADE,blank=True, null=True   )
        society = models.CharField(max_length=250,blank=True, null=True)
        society_code = models.CharField(max_length=250,blank=True, null=True)
        society_pre_code = models.CharField(max_length=250,blank=True, null=True)
        new_society_pre_code = models.CharField(unique=True,max_length=250,blank=True, null=True)
        def __str__(self):
                return str(self.society)
        class Meta:
                verbose_name_plural = "Society"



class farmerTbl(timeStamp):
        first_name = models.CharField(max_length=250,blank=True, null=True)
        last_name = models.CharField(max_length=250,blank=True, null=True)
        farmer_code = models.CharField(max_length=250,blank=True, null=True,unique=True)
        society_name =  models.ForeignKey('societyTbl',on_delete=models.CASCADE,blank=True, null=True  )
        national_id_no = models.CharField(max_length=250,blank=True, null=True)
        contact = models.CharField(max_length=250,blank=True, null=True)
        id_type = models.CharField(max_length=250,blank=True, null=True)
        id_expiry_date  = models.CharField(max_length=250,blank=True, null=True)
        no_of_cocoa_farms = models.IntegerField(max_length=250,blank=True, null=True)
        no_of_certified_crop = models.IntegerField(max_length=250,blank=True, null=True)
        total_cocoa_bags_harvested_previous_year  = models.IntegerField(max_length=250,blank=True, null=True)
        total_cocoa_bags_sold_group_previous_year = models.IntegerField(max_length=250,blank=True, null=True)
        current_year_yeild_estimate = models.IntegerField(max_length=250,blank=True, null=True)
        staffTbl_foreignkey = models.ForeignKey('staffTbl', on_delete=models.CASCADE,blank=True, null=True)
        uuid= models.CharField(max_length=2500,blank=True, null=True)
        farmer_photo = models.ImageField(upload_to="staff" ,blank=True, null=True)
        cal_no_mapped_farms = models.IntegerField(max_length=250,default=0)
        mapped_status= models.CharField(max_length=2500,default="No")
        new_farmer_code= models.CharField(max_length=250,blank=True, null=True,unique=True)
        updated_at = models.DateTimeField(auto_now=True)


        def __str__(self):
                return str(f'{self.first_name} {self.last_name}')

        class Meta:
                verbose_name_plural = "Farmers Details"


class districtStaffTbl(timeStamp):
        staffTbl_foreignkey = models.ForeignKey('staffTbl', on_delete=models.CASCADE)
        districtTbl_foreignkey = models.ForeignKey('districtTbl', on_delete=models.CASCADE)
        class Meta:
                verbose_name_plural = "Staff District Assignments"



class pciTbl(timeStamp):

    STATUS_CHOICES = (
        
        ('high_risk', 'High Risk'),
        ('modium_risk', 'Medium Risk'),
        ('low_risk', 'Low Risk'),
       
    )

    enumerator = models.ForeignKey('districtStaffTbl', on_delete=models.SET_NULL, null=True)
    society = models.ForeignKey('societyTbl', on_delete=models.SET_NULL, null=True)
    access_to_protected_water = models.DecimalField(max_digits=10,decimal_places=2,help_text="Do most households in this community have access to a protected water source?")
    hire_adult_labourers = models.DecimalField(max_digits=10,decimal_places=2,help_text="Do some households in this community hire adult labourers to do agricultural work?")
    awareness_raising_session = models.DecimalField(max_digits=10,decimal_places=2,help_text="Has at least one awareness-raising session on child labour taken place in the community in the past year?")
    women_leaders = models.DecimalField(max_digits=10,decimal_places=2,help_text="Are there any women among the leaders of this community?")
    pre_school = models.DecimalField(max_digits=10,decimal_places=2,help_text="Is there at least one pre-school in this community?")
    primary_school = models.DecimalField(max_digits=10,decimal_places=2,help_text="Is there at least one primary school in this community?")
    separate_toilets = models.DecimalField(max_digits=10,decimal_places=2,help_text="Are there separate toilets for boys and girls in the primary school(s) of the community?")
    provide_food = models.DecimalField(max_digits=10,decimal_places=2,help_text="Do(es) the primary school(s) provide food?")
    scholarships = models.DecimalField(max_digits=10,decimal_places=2,help_text="Do some children in the community access scholarships to attend high school?")
    corporal_punishment = models.DecimalField(max_digits=10,decimal_places=2,help_text="Is there an absence of corporal punishment in the primary school(s)?")
    total_index = models.DecimalField(max_digits=10,decimal_places=2, help_text="Total Index")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='low_risk')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_total_index(self):
    # Convert all fields to decimals before adding
        self.total_index = (
            Decimal(self.access_to_protected_water or 0) +
            Decimal(self.hire_adult_labourers or 0) +
            Decimal(self.awareness_raising_session or 0) +
            Decimal(self.women_leaders or 0) +
            Decimal(self.pre_school or 0) +
            Decimal(self.primary_school or 0) +
            Decimal(self.separate_toilets or 0) +
            Decimal(self.provide_food or 0) +
            Decimal(self.scholarships or 0) +
            Decimal(self.corporal_punishment or 0)
        )
        
        # Convert to float for comparison or use Decimal comparison
        total_float = float(self.total_index)
        
        if total_float <= 4:
            self.status = 'high_risk'
        elif 5 <= total_float <= 6:
            self.status = 'medium_risk'
        else:
            self.status = 'low_risk'
        self.save()

    def __str__(self):
        return f"{self.society}"


class schhoolTbl(timeStamp):
    name = models.CharField(max_length=100)
    pci = models.ForeignKey('pciTbl', on_delete=models.SET_NULL, null=True)
    separate_toilet = models.CharField(max_length=3,help_text="Are there separate toilets for boys and girls in the primary school(s) of the community?")
    food_provided = models.CharField(max_length=3,help_text="Do(es) the primary school(s) provide food?")
    corporal_punishment = models.CharField(max_length=3,help_text="Is there an absence of corporal punishment in the primary school(s)?")

    def __str__(self):
        return f"{self.name}"
    
    
####pass#########################################################################
#Household Survey
#################################################################################

class houseHoldTbl(timeStamp):

    enumerator = models.ForeignKey('districtStaffTbl',on_delete=models.CASCADE,related_name='consent_location',null=True)
    farmer = models.ForeignKey('farmerTbl', on_delete=models.CASCADE, null=True)
    interview_start_time = models.DateTimeField( verbose_name="Interview Start/Pick-up Time", blank=True, null=True)
    gps_point = models.CharField(max_length=100,verbose_name="GPS Point of the Household", blank=True, null=True)
    community_type = models.CharField( max_length=20, choices=COMMUNITY_CHOICES, verbose_name="Type of Community", blank=True, null=True)
    farmer_resides_in_community = models.CharField(null=False,blank=False,choices=YES_OR_NO ,verbose_name="Does the farmer reside in the community stated on the cover?",help_text="Does the farmer reside in the community stated on the cover?")

    # If No, provide the name of the community the farmer resides in.
    # This field expects capital letters and numbers only.
   
    farmer_residing_community = models.CharField(max_length=100,blank=True,help_text="If the farmer does NOT reside in the cover community, provide the community name here.",validators=[community_name_validator])
    farmer_available = models.CharField(null=True,blank=True,choices=YES_OR_NO,verbose_name="Is the farmer available?")
    reason_unavailable = models.CharField(max_length=50,choices=UNAVAILABLE_REASON_CHOICES,blank=True,help_text="If the farmer is not available, select the reason.")
    reason_unavailable_other = models.CharField(max_length=100,blank=True,help_text="If the farmer is not available, provide the reason here.")
    # Who is available to answer for the farmer?
    available_answer_by = models.CharField(max_length=20,choices=ANSWER_BY_CHOICES,blank=True,help_text="Who is available to answer for the farmer?")    
    refusal_toa_participate_reason_survey = models.CharField(max_length=500,blank=True,help_text="If the farmer refused to participate, provide the reason here." )
   
    total_adults = models.PositiveIntegerField(verbose_name="Total number of adults in the household (producer/manager/owner not included)",help_text="Household means people that dwell under the same roof and share the same meal.",validators=[MinValueValidator(1)])
    is_name_correct = models.CharField(choices = CORRECT_RESPONSE_PROVIDED,verbose_name="Is the name of the respondent correct?",help_text="If 'No', please fill in the exact name and surname of the producer.")
    exact_name = models.CharField(max_length=200,blank=True,validators=[allowed_chars_validator],help_text="Exact name and surname of the producer (if respondent name is incorrect).")
    nationality = models.CharField(max_length=20,choices=NATIONALITY_CHOICES,verbose_name="Nationality of the respondent" )
    country_origin = models.CharField(max_length=50,choices=COUNTRY_ORIGIN_CHOICES,blank=True,help_text="If Non Ghanaian, select the country of origin.")
    country_origin_other = models.CharField(max_length=100,blank=True,help_text="If 'Other' is selected, please specify the country of origin.")
    is_owner = models.CharField(choices = CORRECT_RESPONSE_PROVIDED,verbose_name="Is the respondent the owner of the farm?",help_text="If 'No', please fill in the farm's name and details.")
    owner_status_01 = models.CharField(max_length=30,choices=OWNER_STATUS_CHOICES, blank=True,help_text="Which of these best describes you?")
    owner_status_00 = models.CharField(max_length=30,choices=OWNER_STATUS_CHOICES,blank=True,help_text="Which of these best describes you?")
    children_present = models.CharField( choices=YES_OR_NO, verbose_name="Are there children living in the respondent's household?", help_text="Answer Yes if there are children, No otherwise.")
    num_children_5_to_17 = models.PositiveSmallIntegerField(verbose_name="Number of children between ages 5 and 17",validators=[MinValueValidator(1), MaxValueValidator(19)],help_text="Count the producer's children as well as other children living in the household (cannot be negative or exceed 19).")
 
    feedback_enum = models.TextField(help_text="Feedback from enumerator. This field is required.")
    picture_of_respondent = models.ImageField(upload_to='respondent_pictures/',blank=True,null=True,help_text="Picture of the respondent. Required if farmer_available is True.")
    signature_producer = models.ImageField(upload_to='producer_signatures/',blank=True,null=True,help_text="Signature of the producer. Required if farmer_available is True.")
    end_gps = models.CharField(max_length=100,blank=True,null=True,help_text="End GPS coordinates of the survey. Required if sp6_code, farmer_code, and client are set.")
    end_time = models.DateTimeField(blank=True,null=True,help_text="End time of the survey. Required if sp6_code, farmer_code, and client are set.")
    
    sensitized_good_parenting = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Have you sensitized the household members on Good Parenting? (This is mandatory.)")
    sensitized_child_protection = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Have you sensitized the household members on Child Protection? (This is mandatory.)")
    sensitized_safe_labour = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Have you sensitized the household members on Safe Labour Practices? (This is mandatory.)")
    number_of_female_adults = models.PositiveIntegerField(validators=[MinValueValidator(1)],help_text="How many female adults were present during the sensitization? (Must be at least 1.)")
    number_of_male_adults = models.PositiveIntegerField(validators=[MinValueValidator(1)],help_text="How many male adults were present during the sensitization? (Must be at least 1.)")
    picture_of_respondent = models.CharField( max_length=3,choices=YES_NO_CHOICES,help_text="Can you take a picture of the respondent and yourself?")
    picture_sensitization = models.ImageField(upload_to='sensitization/',blank=True,null=True,help_text="Please take a picture of the sensitization being implemented with the family and the child.")
    feedback_observations = models.TextField(blank=True,null=True,help_text="What are your observations regarding the reaction from the parents on the sensitization provided?")
    
    school_fees_owed = models.CharField(max_length=3,choices=SCHOOL_FEES_CHOICES,help_text="Do you owe fees for the school of the children living in your household?")
    parent_remediation = models.CharField(max_length=20,choices=PARENT_REMEDIATION_CHOICES,help_text="What should be done for the parent to stop involving their children in child labour?")
    parent_remediation_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected, specify in capital letters.")
    community_remediation = models.CharField(max_length=30,choices=COMMUNITY_REMEDIATION_CHOICES,help_text="What can be done for the community to stop involving the children in child labour?")
    community_remediation_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected, specify in capital letters.")
    
    owner_name_validator = RegexValidator(regex=r'^[A-Za-z\']+$',message="This field must contain only letters and apostrophes (no spaces or accents).")
    name_owner = models.CharField(max_length=100,validators=[owner_name_validator],verbose_name="Owner's Last Name",blank=True,help_text="Enter the owner's surname. Letters and apostrophes only (no spaces or accents).")
    first_name_owner = models.CharField(max_length=100,validators=[owner_name_validator],verbose_name="Owner's First Name",blank=True,help_text="Enter the owner's first name. Letters and apostrophes only (no spaces or accents).")
    nationality_owner = models.CharField(max_length=20,choices=NATIONALITY_OWNER_CHOICES,verbose_name="What is the nationality of the owner?")
    country_origin_owner = models.CharField(max_length=200,choices=COUNTRY_ORIGIN_OWNER_CHOICES,blank=True,verbose_name="Country of origin of the owner",help_text="If the owner is Non Ghanaian, select the country of origin.")
    country_origin_owner_other = models.CharField(max_length=100,blank=True,verbose_name="Specify country of origin (if Other)",help_text="If 'Other' is selected above, please specify the country.")
    manager_work_length = models.IntegerField(verbose_name="For how many years has the respondent been working for the owner?")

    recruited_workers = models.CharField(choices=YES_OR_NO, verbose_name="Have you recruited at least one worker during the past year?",help_text="Yes or No")
    worker_recruitment_type = models.CharField(max_length=10,choices=WORKER_RECRUITMENT_CHOICES,verbose_name="Do you recruit workers for...")
    worker_agreement_type = models.CharField(max_length=30,choices=WORKER_AGREEMENT_CHOICES,verbose_name="What kind of agreement do you have with your workers?")
    worker_agreement_other = models.CharField(max_length=100,blank=True,verbose_name="Specify other agreement type",help_text="Provide details if 'Other' is selected.")
    tasks_clarified = models.CharField(choices=YES_OR_NO, verbose_name="Were the tasks to be performed by the worker clarified during recruitment?",help_text="Yes or No")
    additional_tasks = models.CharField(choices=YES_OR_NO, verbose_name="Does the worker perform tasks for you or your family members other than those agreed upon?",help_text="Yes or No")
    refusal_action = models.CharField(max_length=20,choices=REFUSAL_ACTION_CHOICES,verbose_name="What do you do when a worker refuses to perform a task?")
    refusal_action_other = models.CharField(max_length=100,blank=True,verbose_name="Specify refusal action",help_text="Fill this if 'Other' is selected.")
    salary_status = models.CharField(max_length=10,choices=SALARY_STATUS_CHOICES,verbose_name="Do your workers receive their full salaries?")
    recruit_1 = models.CharField(max_length=100,choices=YES_OR_NO,verbose_name="It is acceptable for a person who cannot pay their debts to work for the creditor to reimburse the debt.")
    recruit_2 = models.CharField(max_length=100,choices=YES_OR_NO,verbose_name="It is acceptable for an employer not to reveal the true nature of the work during recruitment.")
    recruit_3 = models.CharField(max_length=100,choices=YES_OR_NO,verbose_name="A worker is obliged to work whenever he is called upon by his employer.")
    conditions_1 = models.CharField(max_length=100,choices=AGREE_OR_DISAGREE,verbose_name="A worker is not entitled to move freely.")
    conditions_2 = models.CharField(max_length=100,choices=AGREE_OR_DISAGREE,verbose_name="A worker must be free to communicate with his or her family and friends.")
    conditions_3 = models.CharField(max_length=100,choices=AGREE_OR_DISAGREE,verbose_name="A worker is obliged to adapt to any living conditions imposed by the employer.")
    conditions_4 = models.CharField(max_length=100,choices=AGREE_OR_DISAGREE,verbose_name="It is acceptable for an employer and their family to interfere in a worker's private life.")
    conditions_5 = models.CharField( max_length=100, choices=AGREE_OR_DISAGREE, verbose_name="A worker should not have the freedom to leave work whenever they wish.")
    leaving_1 = models.CharField(max_length=100,choices=AGREE_OR_DISAGREE,verbose_name="A worker should be required to stay longer than expected while waiting for unpaid salary.")
    leaving_2 = models.CharField(max_length=100,choices=AGREE_OR_DISAGREE,verbose_name="A worker should not be able to leave their employer when they owe money to their employer.")
    consent_recruitment = models.CharField(max_length=100,choices=AGREE_OR_DISAGREE,verbose_name="It is acceptable to recruit someone for work without their consent.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        



class AdultHouseholdMember(timeStamp):

    houseHold = models.ForeignKey('houseHoldTbl', on_delete=models.CASCADE, related_name="members")

    full_name = models.CharField(max_length=200, verbose_name="Full Name", help_text="Enter full name without special characters.",validators=[name_validator])
    relationship = models.CharField(max_length=50,choices=RELATIONSHIP_CHOICES,verbose_name="Relationship to the respondent")
    relationship_other = models.CharField(max_length=100,blank=True,verbose_name="Specify relationship (if Other)",help_text="If 'Other' is selected, please specify.")
    gender = models.CharField(max_length=6,choices=GENDER_CHOICES,verbose_name="Gender")
    nationality = models.CharField(max_length=20,choices=NATIONALITY_CHOICES,verbose_name="Nationality")
    country_origin = models.CharField(max_length=50,choices=COUNTRY_ORIGIN_CHOICES,blank=True,verbose_name="Country of origin (if Non Ghanaian)")
    country_origin_other = models.CharField(max_length=100,blank=True,verbose_name="Specify country of origin (if Other)")
    year_birth = models.IntegerField(verbose_name="Year of birth",validators=[MinValueValidator(1900),MaxValueValidator(datetime.now().year)])
    birth_certificate = models.CharField( max_length=3, choices=BIRTH_CERTIFICATE_CHOICES,verbose_name="Does this member have a birth certificate?")
    main_work = models.CharField( max_length=30, choices=MAIN_WORK_CHOICES, verbose_name="Main work/occupation")
    main_work_other = models.CharField(max_length=100,blank=True,verbose_name="Specify main work (if Other)",help_text="If 'Other' is selected, please specify." )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.full_name} (Household {self.household.id})"

    #################################################################################
    # CHILDREN IN THE RESPONDENT'S HOUSEHOLD MODEL
    #################################################################################



class ChildInHouseholdTbl(timeStamp):
       # Gender choices
    houseHold = models.ForeignKey('houseHoldTbl', on_delete=models.CASCADE, related_name='children')

    child_declared_in_cover = models.CharField(choices=YES_NO_CHOICES,verbose_name="Is the child among those declared in the cover as the farmer's child?",help_text="Yes if the child is already listed in the cover; No otherwise.")
    child_identifier = models.PositiveSmallIntegerField(verbose_name="Child identifier",validators=[MinValueValidator(1), MaxValueValidator(19)],help_text="Enter the number attached to the child's name in the cover (must be less than 20).")
    child_can_be_surveyed = models.CharField(choices=YES_NO_CHOICES,verbose_name="Can the child be surveyed now?",help_text="Answer Yes if the child is available for survey; No otherwise.")
    child_unavailability_reason = models.CharField(max_length=20,choices=CHILD_UNAVAILABILITY_REASON_CHOICES,blank=True,verbose_name="Reason for child not being surveyed",help_text="Select the reason if the child cannot be surveyed.")
    child_not_avail = models.CharField(max_length=200,blank=True,  verbose_name="Other reasons (in capital letters) for child not being available", help_text="Provide reasons in capital letters. (Minimum length can be validated separately.)")
    who_answers_child_unavailable = models.CharField(max_length=20,choices=WHO_ANSWERS_CHOICES,blank=True,verbose_name="Who is answering for the child (if not available)")
    who_answers_child_unavailable_other = models.CharField(max_length=100,blank=True,verbose_name="Specify who is answering (if Other is selected)")
    child_first_name = models.CharField(max_length=100,validators=[words_validator],verbose_name="Child's First Name")
    child_surname = models.CharField(max_length=100,validators=[words_validator],verbose_name="Child's Surname" )
    child_gender = models.CharField(max_length=4,choices=GENDER_CHOICES,verbose_name="Gender of the Child")
    child_year_birth = models.IntegerField(verbose_name="Year of Birth of the Child",validators=[MinValueValidator(2007), MaxValueValidator(2020)],help_text="The year must be between 2007 and 2020 (child must be between 5 and 17 years old).")
    child_birth_certificate = models.CharField(max_length=3,choices=BIRTH_CERTIFICATE_CHOICES,verbose_name="Does the child have a birth certificate?")
    child_birth_certificate_reason = models.CharField(max_length=200,blank=True,verbose_name="If no, please specify why",help_text="Provide a reason if the child does not have a birth certificate.")
    
    child_born_in_community = models.CharField(max_length=20, choices=CHILD_BORN_CHOICES, verbose_name="Is the child born in this community?", help_text="Select an option.")  
    child_country_of_birth = models.CharField(max_length=20, choices=COUNTRY_OF_BIRTH_CHOICES, blank=True, verbose_name="In which country is the child born?", help_text="Provide this only if 'No, born in another country' is selected.")  
    child_country_of_birth_other = models.CharField(max_length=100, blank=True, verbose_name="Specify country of birth (if Other)", help_text="Use capital letters without special characters.", validators=[capital_letters_numbers_validator])  
    child_relationship_to_head = models.CharField(max_length=50, choices=CHILD_RELATIONSHIP_CHOICES, verbose_name="Relationship of the child to the head of the household")  
    child_relationship_to_head_other = models.CharField(max_length=100, blank=True, verbose_name="Specify relationship (if Other)", help_text="Write in capital letters without special characters.", validators=[capital_letters_numbers_validator])  
    child_not_live_with_family_reason = models.CharField(max_length=50, choices=CHILD_NOT_LIVE_REASONS, blank=True, verbose_name="Why does the child not live with his/her family?")  
    child_not_live_with_family_reason_other = models.CharField(max_length=200, blank=True, verbose_name="Other reason (if Other is selected)")  
    child_decision_maker = models.CharField(max_length=30, choices=CHILD_DECISION_MAKER_CHOICES, verbose_name="Who decided that the child comes into the household?")  
    child_decision_maker_other = models.CharField(max_length=100, blank=True, verbose_name="Specify decision maker (if Other is selected)")  
    child_agree_with_decision = models.CharField(max_length=3, choices=YES_NO_CHOICES, verbose_name="Did the child agree with this decision?")  
    child_seen_parents = models.CharField(max_length=3, choices=YES_NO_CHOICES, verbose_name="Has the child seen and/or spoken with his/her parents in the past year?")  
    child_last_seen_parent = models.CharField(max_length=20, choices=LAST_SEEN_CHOICES, verbose_name="When was the last time the child saw/talked with a parent?")  
    child_living_duration = models.CharField(max_length=20, choices=LIVING_DURATION_CHOICES, verbose_name="For how long has the child been living in the household?")  
    child_accompanied_by = models.CharField(max_length=20, choices=CHILD_ACCOMPANIED_CHOICES, verbose_name="Who accompanied the child to come here?")  
    child_accompanied_by_other = models.CharField(max_length=100, blank=True, verbose_name="Specify accompaniment (if Other is selected)")  

    ############################################
    # ChildEducationDetails Model   
    ############################################
    # Model fields
    child_father_location = models.CharField(max_length=50, choices=FATHER_LOCATION_CHOICES, null=True, blank=True, help_text="Where does the child's father live?")
    child_father_country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, null=True, blank=True, help_text="Father's country of residence.")
    child_father_country_other = models.CharField(max_length=100, null=True, blank=True, help_text="If 'Other' is selected, specify the country (in capital letters).")
    child_mother_location = models.CharField(max_length=50, choices=FATHER_LOCATION_CHOICES, null=True, blank=True, help_text="Where does the child's mother live?")
    child_mother_country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, null=True, blank=True, help_text="Mother's country of residence.")
    child_mother_country_other = models.CharField(max_length=100, null=True, blank=True, help_text="If 'Other' is selected, specify the country (in capital letters).")
    child_educated = models.IntegerField(choices=EDUCATION_STATUS_CHOICES, help_text="Is the child currently enrolled in school? (1 = Yes, 0 = No)")
    child_school_name = models.CharField(max_length=200, null=True, blank=True, help_text="Name of the school (if enrolled).")
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPE_CHOICES, null=True, blank=True, help_text="Is the school public or private?")
    child_grade = models.CharField(max_length=10, choices=GRADE_CHOICES, null=True, blank=True, help_text="What grade is the child enrolled in?")
    sch_going_times = models.IntegerField(choices=SCHOOL_GOING_TIMES_CHOICES, null=True, blank=True, help_text="How many times does the child go to school in a week?")
    basic_need_available = models.CharField(max_length=100, null=True, blank=True, help_text="Comma-separated basic needs available (e.g., books, bag, pen, uniform, shoes, none).")
    child_schl2 = models.IntegerField(choices=SCHL2_CHOICES, null=True, blank=True, help_text="Has the child ever been to school (if not currently enrolled)?")
    child_schl_left_age = models.IntegerField(null=True, blank=True, help_text="Which year did the child leave school? (Or the age at which they left)")

    #################################################################################
    # CHILD EDUCATIONAL ASSESSMENT MODEL
    #################################################################################
  
    calculation_response = models.CharField(max_length=20,choices=CALCULATION_RESPONSE_CHOICES,help_text="Response to the calculation task.")
    reading_response = models.CharField(max_length=20,choices=READING_RESPONSE_CHOICES,help_text="Response to the reading task.")
    writing_response = models.CharField(max_length=20,choices=WRITING_RESPONSE_CHOICES,help_text="Response to the writing task.")
    education_level = models.CharField(max_length=30,choices=EDUCATION_LEVEL_CHOICES,help_text="What is the education level of the child?")
    child_schl_left_why = models.CharField(max_length=20,choices=SCHOOL_LEFT_REASON_CHOICES,null=True,blank=True,help_text="What is the main reason for the child leaving school?")
    child_schl_left_why_other = models.CharField(max_length=200,null=True,blank=True,help_text="Specify the reason if 'Other' is selected.")
    child_why_no_school = models.CharField(max_length=20,choices=NEVER_SCHOOL_REASON_CHOICES,null=True,blank=True,help_text="Why has the child never been to school?")
    child_why_no_school_other = models.CharField(max_length=200,null=True,blank=True,help_text="Specify the reason if 'Other' is selected.")
    child_school_7days = models.CharField(max_length=3, choices=SCHOOL_7DAYS_CHOICES, null=True,blank=True,help_text="Has the child been to school in the past 7 days?")
    child_school_absence_reason = models.CharField(max_length=20,choices=SCHOOL_ABSENCE_REASON_CHOICES,null=True,blank=True,help_text="If not, why has the child not been to school?")
    child_school_absence_reason_other = models.CharField(max_length=200,null=True,blank=True,help_text="Specify the reason if 'Other' is selected.")
    missed_school = models.CharField( max_length=3,choices=MISSED_SCHOOL_CHOICES,help_text="Has the child missed school days in the past 7 days? (Mandatory if basic_need_available is not null)")
    missed_school_reason = models.CharField(max_length=20,choices=MISSED_SCHOOL_REASON_CHOICES,null=True,blank=True,help_text="Why did the child miss school? (Only applicable if missed_school is 'yes')")
    missed_school_reason_other = models.CharField(max_length=200,null=True,blank=True,help_text="If 'Other' is selected for why the child missed school, please specify.")
    work_in_house = models.CharField(max_length=3,choices=WORK_IN_HOUSE_CHOICES,help_text="In the past 7 days, has the child worked in the house? (Mandatory if child_educated is not null)")
    work_on_cocoa = models.CharField(max_length=3,choices=WORK_ON_COCOA_CHOICES,help_text="In the past 7 days, has the child been working on the cocoa farm? (Mandatory if child_work_house is not null)")
    work_frequency = models.CharField(max_length=10,choices=WORK_FREQUENCY_CHOICES,null=True,blank=True ,help_text="How often has the child worked in the past 7 days? (Mandatory if work_in_house or work_on_cocoa is 'yes')")
    observed_work = models.CharField(max_length=3, choices=OBSERVED_WORK_CHOICES, null=True, blank=True, help_text="Did the enumerator observe the child working in a real situation? (Only applicable if work_in_house is 'yes')")
    # performed_tasks = models.CharField(max_length=500,null=True,blank=True,help_text="Which of these tasks has the child performed in the last 7 days? ""If multiple, separate using commas.")
    # Alternatively, if you install and use django-multiselectfield, you might do:
    performed_tasks = MultiSelectField(choices=TASK_CHOICES, max_length=500, help_text="Select tasks performed in the last 7 days")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    



class lightTaskTbl(timeStamp):
   name = models.CharField(max_length=100)
   

class heavyTaskTbl(timeStamp):
   name = models.CharField(max_length=100)


class childLightTaskTbl(timeStamp):
    task = models.ForeignKey('lightTaskTbl', on_delete=models.CASCADE)
    child = models.ForeignKey('ChildInHouseholdTbl', on_delete=models.CASCADE)

    remuneration_received_12months = models.CharField(max_length=3, choices=REMUNERATION_CHOICES, help_text="Did the child receive remuneration for the activity %rostertitle%?")
    light_duty_duration_school_12 = models.CharField(max_length=10,choices=LIGHT_DUTY_DURATION_SCHOOL_CHOICES,help_text="Longest time spent on light duty during a SCHOOL DAY in the last 7 days.")
    light_duty_duration_non_school_12 = models.CharField(max_length=10,choices=LIGHT_DUTY_DURATION_NON_SCHOOL_CHOICES,help_text="Longest time spent on light duty during a NON-SCHOOL DAY in the last 7 days.")
    task_location_12 = models.CharField(max_length=20,choices=TASK_LOCATION_CHOICES,help_text="Where was this task done?")
    task_location_other_12 = models.CharField(max_length=200,null=True,blank=True,help_text="If 'Other' is selected, please specify.")
    total_hours_light_work_school_12 = models.IntegerField(help_text="Total hours spent in light work during SCHOOL DAYS in the past 7 days. Must be between 0 and 1015.")
    total_hours_light_work_non_school_12 = models.IntegerField(help_text="Total hours spent in light work during NON-SCHOOL DAYS in the past 7 days. Must be between 0 and 1015.")
    under_supervision_12 = models.CharField(max_length=3,choices=SUPERVISION_CHOICES,help_text="Was the child under supervision of an adult when performing this task?")
    tasks_done_in_7days = models.CharField(max_length=500,blank=True,help_text="Which of the following tasks has the child done in the last 7 days on the cocoa farm? ""If multiple tasks apply, list the keys separated by commas.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
class childHeavyTaskTbl(timeStamp):
    task = models.ForeignKey('heavyTaskTbl', on_delete=models.CASCADE)
    child = models.ForeignKey('ChildInHouseholdTbl', on_delete=models.CASCADE)

    salary_received = models.CharField(max_length=3,choices=SALARY_CHOICES,help_text="Has the child received a salary for this task?")
    task_location = models.CharField(max_length=20,choices=TASK_LOCATION_CHOICES,help_text="Where was this task done?")
    task_location_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected, please specify.")
    longest_time_school_day = models.CharField(max_length=20,choices=DURATION_CHOICES_SCHOOL,help_text="What was the longest time spent on the task during a SCHOOL DAY in the last 7 days?")
    longest_time_non_school_day = models.CharField(max_length=20,choices=DURATION_CHOICES_NON_SCHOOL,help_text="What was the longest time spent on the task during a NON-SCHOOL DAY in the last 7 days?")
    total_hours_school_days = models.IntegerField(help_text="How many hours has the child worked on during SCHOOL DAYS in the last 7 days? (0 to 1015 hours)")
    total_hours_non_school_days = models.IntegerField(help_text="How many hours has the child been working on during NON-SCHOOL DAYS in the last 7 days? (0 to 1015 hours)")
    under_supervision = models.CharField(max_length=3, choices=SUPERVISION_CHOICES, help_text="Was the child under supervision of an adult when performing this task?")
    heavy_tasks_12months = models.CharField(max_length=500,blank=True,help_text="Which of the following tasks has the child performed in the last 12 months on the cocoa farm? ""If multiple tasks apply, list the keys separated by commas.")
    salary_received_12 = models.CharField(max_length=3,choices=SALARY_CHOICES,help_text="Has the child received a salary for this task?")
    task_location_12 = models.CharField(max_length=20,choices=TASK_LOCATION_CHOICES,help_text="Where was this task done?")
    task_location_other_12 = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected, please specify.")
    longest_time_school_day = models.CharField(max_length=10,choices=LONGEST_TIME_SCHOOL_DAY_CHOICES,help_text="Longest time spent on the task during a SCHOOL DAY in the last 7 days.")
    longest_time_non_school_day = models.CharField(max_length=10,choices=LONGEST_TIME_NON_SCHOOL_DAY_CHOICES,help_text="Longest time spent on the task during a NON-SCHOOL DAY in the last 7 days.")
    total_hours_school_days = models.IntegerField(help_text="How many hours has the child worked on during SCHOOL DAYS in the last 7 days? (0-1015)")
    total_hours_non_school_days = models.IntegerField(help_text="How many hours has the child been working on during NON-SCHOOL DAYS in the last 7 days? (0-1015)")
    under_supervision = models.CharField( max_length=3, choices=YES_NO_CHOICES, help_text="Was the child under supervision of an adult when performing this task?")
    child_work_who = models.CharField(max_length=20,choices=WORK_FOR_WHOM_CHOICES,help_text="For whom does the child work?")
    child_work_who_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected, please specify.")
    child_work_why = models.CharField(max_length=20,choices=WORK_REASON_CHOICES,help_text="Why does the child work?")
    child_work_why_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected for why the child works, please specify (in capital letters).")
    agrochemicals_applied = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Has the child ever applied or sprayed agrochemicals on the farm?")
    child_on_farm_during_agro = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Was the child on the farm during the application of agrochemicals?")
    suffered_injury = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Recently, has the child suffered any injury?")
    wound_cause = models.CharField(max_length=30,choices=INJURY_CAUSE_CHOICES,blank=True,null=True,help_text="How did the child get wounded? (If injured)")
    wound_cause_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected, please specify.")
    wound_time = models.CharField(max_length=20,choices=WOUND_TIME_CHOICES,blank=True,null=True,help_text="When was the child wounded? (If injured)")
    child_often_pains = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Does the child often feel pains or aches?")
    help_child_health = models.CharField(max_length=200,blank=True,null=True,help_text="What help did the child receive to get better? (Select all that apply, separated by commas)")
    help_child_health_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected above, please specify.")
    child_photo = models.ImageField(upload_to='child_photos/',blank=True,null=True,help_text="Upload a photo of the child (if available).")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

class childLightTask12MonthsTbl(timeStamp):
    child = models.ForeignKey('ChildInHouseholdTbl', on_delete=models.CASCADE) 
    task = models.ForeignKey('lightTaskTbl', on_delete=models.CASCADE)
    
    remuneration_received = models.CharField(max_length=3,choices=REMUNERATION_CHOICES,help_text="Did the child receive remuneration for the activity?")
    light_duty_duration_school = models.CharField(max_length=10,choices=LIGHT_DUTY_DURATION_CHOICES,help_text="What was the longest time spent on light duty during a SCHOOL DAY in the last 7 days?")
    light_duty_duration_non_school = models.CharField(max_length=10,choices=LIGHT_DUTY_DURATION_NON_SCHOOL_CHOICES,help_text="What was the longest amount of time spent on light duty on a NON-SCHOOL DAY in the last 7 days?")
    task_location = models.CharField(max_length=20,choices=TASK_LOCATION_CHOICES,help_text="Where was this task done?")
    task_location_other = models.CharField(max_length=200,null=True,blank=True,help_text="If 'Other' is selected, please specify.")
    total_hours_light_work_school = models.IntegerField(help_text="How many hours in total did the child spend in light work during SCHOOL DAYS in the past 7 days?")
    total_hours_light_work_non_school = models.IntegerField(help_text="How many hours in total did the child spend on light duty during NON-SCHOOL DAYS in the past 7 days?")
    under_supervision = models.CharField(max_length=3,choices=SUPERVISION_CHOICES,help_text="Was the child under supervision of an adult when performing this task?")
    performed_tasks_12months = MultiSelectField(max_length=500,null=True,blank=True,help_text="Which of these tasks has child %rostertitle% performed in the last 12 months? ""If multiple tasks, separate their keys using commas.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class childHeavyTask12MonthsTbl(timeStamp):
    child = models.ForeignKey('ChildInHouseholdTbl', on_delete=models.CASCADE) 
    task = models.ForeignKey('heavyTaskTbl', on_delete=models.CASCADE)
    salary_received = models.CharField(max_length=3,choices=SALARY_CHOICES,help_text="Has the child received a salary for this task?")
    task_location = models.CharField(max_length=20,choices=TASK_LOCATION_CHOICES,help_text="Where was this task done?")
    task_location_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected, please specify.")
    longest_time_school_day = models.CharField(max_length=20,choices=DURATION_CHOICES_SCHOOL,help_text="What was the longest time spent on the task during a SCHOOL DAY in the last 7 days?")
    longest_time_non_school_day = models.CharField(max_length=20,choices=DURATION_CHOICES_NON_SCHOOL,help_text="What was the longest time spent on the task during a NON-SCHOOL DAY in the last 7 days?")
    total_hours_school_days = models.IntegerField(help_text="How many hours has the child worked on during SCHOOL DAYS in the last 7 days? (0 to 1015 hours)")
    total_hours_non_school_days = models.IntegerField(help_text="How many hours has the child been working on during NON-SCHOOL DAYS in the last 7 days? (0 to 1015 hours)")
    under_supervision = models.CharField(max_length=3, choices=SUPERVISION_CHOICES, help_text="Was the child under supervision of an adult when performing this task?")
    heavy_tasks_12months = models.CharField(max_length=500,blank=True,help_text="Which of the following tasks has the child performed in the last 12 months on the cocoa farm? ""If multiple tasks apply, list the keys separated by commas.")
    salary_received_12 = models.CharField(max_length=3,choices=SALARY_CHOICES,help_text="Has the child received a salary for this task?")
    task_location_12 = models.CharField(max_length=20,choices=TASK_LOCATION_CHOICES,help_text="Where was this task done?")
    task_location_other_12 = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected, please specify.")
    longest_time_school_day = models.CharField(max_length=10,choices=LONGEST_TIME_SCHOOL_DAY_CHOICES,help_text="Longest time spent on the task during a SCHOOL DAY in the last 7 days.")
    longest_time_non_school_day = models.CharField(max_length=10,choices=LONGEST_TIME_NON_SCHOOL_DAY_CHOICES,help_text="Longest time spent on the task during a NON-SCHOOL DAY in the last 7 days.")
    total_hours_school_days = models.IntegerField(help_text="How many hours has the child worked on during SCHOOL DAYS in the last 7 days? (0-1015)")
    total_hours_non_school_days = models.IntegerField(help_text="How many hours has the child been working on during NON-SCHOOL DAYS in the last 7 days? (0-1015)")
    under_supervision = models.CharField( max_length=3, choices=YES_NO_CHOICES, help_text="Was the child under supervision of an adult when performing this task?")
    child_work_who = models.CharField(max_length=20,choices=WORK_FOR_WHOM_CHOICES,help_text="For whom does the child work?")
    child_work_who_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected, please specify.")
    child_work_why = models.CharField(max_length=20,choices=WORK_REASON_CHOICES,help_text="Why does the child work?")
    child_work_why_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected for why the child works, please specify (in capital letters).")
    agrochemicals_applied = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Has the child ever applied or sprayed agrochemicals on the farm?")
    child_on_farm_during_agro = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Was the child on the farm during the application of agrochemicals?")
    suffered_injury = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Recently, has the child suffered any injury?")
    wound_cause = models.CharField(max_length=30,choices=INJURY_CAUSE_CHOICES,blank=True,null=True,help_text="How did the child get wounded? (If injured)")
    wound_cause_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected, please specify.")
    wound_time = models.CharField(max_length=20,choices=WOUND_TIME_CHOICES,blank=True,null=True,help_text="When was the child wounded? (If injured)")
    child_often_pains = models.CharField(max_length=3,choices=YES_NO_CHOICES,help_text="Does the child often feel pains or aches?")
    help_child_health = models.CharField(max_length=200,blank=True,null=True,help_text="What help did the child receive to get better? (Select all that apply, separated by commas)")
    help_child_health_other = models.CharField(max_length=200,blank=True,null=True,help_text="If 'Other' is selected above, please specify.")
    child_photo = models.ImageField(upload_to='child_photos/',blank=True,null=True,help_text="Upload a photo of the child (if available).")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

##############################################################################################################################################################################################################


# Add these models to your existing models.py

class QueryCategory(timeStamp):
    """
    Description: Categories for queries (e.g., Data Quality, Follow-up Required, Clarification Needed)
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Query Categories"


class QueryPriority(timeStamp):
    """
    Description: Priority levels for queries (e.g., High, Medium, Low)
    """
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#007bff')  # Hex color code
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Query Priorities"


class QueryStatus(timeStamp):
    """
    Description: Status options for queries (e.g., Open, In Progress, Resolved, Closed)
    """
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#6c757d')  # Hex color code
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Query Statuses"


class Query(timeStamp):
    """
    Description: Main query model for communication between supervisors and enumerators
    """
    query_id = models.CharField(max_length=20, unique=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(QueryCategory, on_delete=models.CASCADE)
    priority = models.ForeignKey(QueryPriority, on_delete=models.CASCADE)
    status = models.ForeignKey(QueryStatus, on_delete=models.CASCADE, default=1)  # Default to Open
    
    # Relationships
    assigned_to = models.ForeignKey(staffTbl, on_delete=models.CASCADE, related_name='assigned_queries')
    created_by = models.ForeignKey(staffTbl, on_delete=models.CASCADE, related_name='created_queries')
    household = models.ForeignKey(houseHoldTbl, on_delete=models.CASCADE, null=True, blank=True)
    farmer = models.ForeignKey(farmerTbl, on_delete=models.CASCADE, null=True, blank=True)
    child = models.ForeignKey(ChildInHouseholdTbl, on_delete=models.CASCADE, null=True, blank=True)
    
    # Dates
    due_date = models.DateTimeField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    # Flags
    requires_follow_up = models.BooleanField(default=False)
    is_escalated = models.BooleanField(default=False)
    escalated_to = models.ForeignKey(staffTbl, on_delete=models.SET_NULL, null=True, blank=True, related_name='escalated_queries')
    
    def __str__(self):
        return f"{self.query_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.query_id:
            # Generate query ID
            self.query_id = self.generate_query_id()
        super().save(*args, **kwargs)
    
    def generate_query_id(self):
        """
        Generate query ID in format QRY-YYYYMMDD-XXX
        """
        date_str = timezone.now().strftime('%Y%m%d')
        last_query = Query.objects.filter(query_id__startswith=f'QRY-{date_str}').order_by('-query_id').first()
        
        if last_query:
            try:
                last_number = int(last_query.query_id.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"QRY-{date_str}-{next_number:03d}"
    
    @property
    def is_overdue(self):
        if self.due_date and self.status.name != 'Resolved' and self.status.name != 'Closed':
            return timezone.now() > self.due_date
        return False
    
    class Meta:
        verbose_name_plural = "Queries"
        ordering = ['-created_date']


class QueryResponse(timeStamp):
    """
    Description: Responses to queries from enumerators
    """
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='responses')
    responded_by = models.ForeignKey(staffTbl, on_delete=models.CASCADE)
    response_text = models.TextField()
    attachment = models.FileField(upload_to='query_responses/', null=True, blank=True)
    
    def __str__(self):
        return f"Response to {self.query.query_id}"
    
    class Meta:
        verbose_name_plural = "Query Responses"
        ordering = ['created_date']


class QueryAttachment(timeStamp):
    """
    Description: Attachments for queries (images, documents, etc.)
    """
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='query_attachments/')
    file_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(staffTbl, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.file_name
    
    class Meta:
        verbose_name_plural = "Query Attachments"


class FlaggedIssue(timeStamp):
    """
    Description: Issues flagged for review
    """
    FLAG_TYPES = (
        ('data_quality', 'Data Quality Issue'),
        ('child_labour', 'Child Labour Concern'),
        ('safety', 'Safety Concern'),
        ('ethical', 'Ethical Concern'),
        ('other', 'Other'),
    )
    
    flag_id = models.CharField(max_length=20, unique=True, blank=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='flags')
    flag_type = models.CharField(max_length=20, choices=FLAG_TYPES)
    description = models.TextField()
    severity = models.CharField(max_length=20, choices=(
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ))
    flagged_by = models.ForeignKey(staffTbl, on_delete=models.CASCADE, related_name='flagged_issues')
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(staffTbl, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_issues')
    review_notes = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.flag_id} - {self.get_flag_type_display()}"
    
    def save(self, *args, **kwargs):
        if not self.flag_id:
            self.flag_id = self.generate_flag_id()
        super().save(*args, **kwargs)
    
    def generate_flag_id(self):
        """
        Generate flag ID in format FLG-YYYYMMDD-XXX
        """
        date_str = timezone.now().strftime('%Y%m%d')
        last_flag = FlaggedIssue.objects.filter(flag_id__startswith=f'FLG-{date_str}').order_by('-flag_id').first()
        
        if last_flag:
            try:
                last_number = int(last_flag.flag_id.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"FLG-{date_str}-{next_number:03d}"
    
    class Meta:
        verbose_name_plural = "Flagged Issues"
        ordering = ['-created_date']


class Escalation(timeStamp):
    """
    Description: Cases escalated to supervisors
    """
    ESCALATION_TYPES = (
        ('technical', 'Technical Issue'),
        ('managerial', 'Managerial Decision'),
        ('safety', 'Safety Concern'),
        ('ethical', 'Ethical Issue'),
        ('other', 'Other'),
    )
    
    escalation_id = models.CharField(max_length=20, unique=True, blank=True)
    query = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='escalations')
    escalation_type = models.CharField(max_length=20, choices=ESCALATION_TYPES)
    reason = models.TextField()
    escalated_by = models.ForeignKey(staffTbl, on_delete=models.CASCADE, related_name='escalations_made')
    escalated_to = models.ForeignKey(staffTbl, on_delete=models.CASCADE, related_name='escalations_received')
    priority = models.ForeignKey(QueryPriority, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True, null=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.escalation_id} - {self.get_escalation_type_display()}"
    
    def save(self, *args, **kwargs):
        if not self.escalation_id:
            self.escalation_id = self.generate_escalation_id()
        super().save(*args, **kwargs)
    
    def generate_escalation_id(self):
        """
        Generate escalation ID in format ESC-YYYYMMDD-XXX
        """
        date_str = timezone.now().strftime('%Y%m%d')
        last_esc = Escalation.objects.filter(escalation_id__startswith=f'ESC-{date_str}').order_by('-escalation_id').first()
        
        if last_esc:
            try:
                last_number = int(last_esc.escalation_id.split('-')[-1])
                next_number = last_number + 1
            except (ValueError, IndexError):
                next_number = 1
        else:
            next_number = 1
        
        return f"ESC-{date_str}-{next_number:03d}"
    
    @property
    def is_overdue(self):
        if not self.resolved:
            return timezone.now() > self.due_date
        return False
    
    class Meta:
        verbose_name_plural = "Escalations"
        ordering = ['-created_date']


##########################################################################################################################################


# Add these models to your existing models.py

class RiskAssessment(timeStamp):
    """
    Description: Main risk assessment model for children
    """
    RISK_LEVELS = (
        ('no_risk', 'No Risk'),
        ('light_risk', 'Light Task Risk'),
        ('heavy_risk', 'Heavy Task Risk'),
        ('both_risk', 'Both Light and Heavy Task Risk'),
    )
    
    child = models.OneToOneField('ChildInHouseholdTbl', on_delete=models.CASCADE, related_name='risk_assessment')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='no_risk')
    assessment_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Risk Assessment for {self.child} - {self.get_risk_level_display()}"
    
    class Meta:
        verbose_name_plural = "Risk Assessments"
        ordering = ['-assessment_date']


class HeavyTaskRisk(timeStamp):
    """
    Description: Records heavy task risks for children
    """
    risk_assessment = models.ForeignKey(RiskAssessment, on_delete=models.CASCADE, related_name='heavy_task_risks')
    task = models.ForeignKey('heavyTaskTbl', on_delete=models.CASCADE)
    task_name = models.CharField(max_length=100)
    risk_detected_date = models.DateTimeField(auto_now_add=True)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Heavy Task Risk: {self.task_name} for {self.risk_assessment.child}"
    
    class Meta:
        verbose_name_plural = "Heavy Task Risks"


class LightTaskRisk(timeStamp):
    """
    Description: Records light task risks for children with detailed criteria
    """
    risk_assessment = models.ForeignKey(RiskAssessment, on_delete=models.CASCADE, related_name='light_task_risks')
    task = models.ForeignKey('lightTaskTbl', on_delete=models.CASCADE)
    task_name = models.CharField(max_length=100)
    risk_detected_date = models.DateTimeField(auto_now_add=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_supervised = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    child_age = models.IntegerField()
    meets_criteria = models.BooleanField(default=False)
    criteria_details = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Light Task Risk: {self.task_name} for {self.risk_assessment.child}"
    
    class Meta:
        verbose_name_plural = "Light Task Risks"


class RiskAssessmentHistory(timeStamp):
    """
    Description: Tracks history of risk assessments for audit purposes
    """
    risk_assessment = models.ForeignKey(RiskAssessment, on_delete=models.CASCADE, related_name='history')
    previous_risk_level = models.CharField(max_length=20)
    new_risk_level = models.CharField(max_length=20)
    changed_by = models.ForeignKey('staffTbl', on_delete=models.SET_NULL, null=True)
    change_reason = models.TextField(blank=True, null=True)
    change_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Risk change: {self.previous_risk_level} → {self.new_risk_level}"
    
    class Meta:
        verbose_name_plural = "Risk Assessment History"
        ordering = ['-change_date']






###################################################################################################

