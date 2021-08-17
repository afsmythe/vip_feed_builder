from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.forms import model_to_dict, fields_for_model
from lxml import etree
from lxml.etree import Element
import pprint


def xml_element(model):
    sequence = fields_for_model(model, exclude = ['id']).keys()
    dict = model_to_dict(model, exclude = ['id'])
    element = etree.Element(model.__class__.__name__, attrib = {'id': str(model.id)})
    e_dict = dict
    #e_dict = self.dict()
    for i in sequence:
        key, val = i, e_dict[i]
    #for key, val in e_dict.items():
        if isinstance(val, list) and len(val) > 0:
            #print(val)
            child = Element(key)
            l = []
            for i in val:
                #check if type is a sub-type.
                if isinstance(i, InternationalizedText):
                    #todo add .xml() method to InternationalizedText model
                    it_child = Element('Text', attrib = {'language': i.Language})
                    it_child.text = i.LanguageString
                    child.append(it_child)
                    element.append(child)
                elif isinstance(i, ExternalIdentifier):
                    for ed in val:
                        child = Element(key)
                        child.append(ed.xml())
                elif isinstance(i, LatLng):
                    latlng = LatLng.objects.get(id = i.id)
                    child = latlng.xml()
                    element.append(child)
                elif isinstance(i, Schedule):
                    print('Schedule found')
                    schedule = Schedule.objects.get(id = i.id)
                    child = schedule.xml()
                    element.append(child)
                elif isinstance(i, SimpleAddressType):
                    print('Structured Address')
                    structuredaddress = SimpleAddressType.objects.get(id = i.id)
                    child = structuredaddress.xml()
                    element.append(child)
                elif isinstance(i, ElectionNotice):
                    print('Election Notice')
                    notice = ElectionNotice.objects.get(id = i.id)
                    child = notice.xml()
                    element.append(child)
                else:
                    #it is not a sub-type, is IDXREFS
                    l.append(str(i.id))
            child.text = " ".join(l)
            element.append(child)
        else:
            if key == 'Date':
                date = Element('Date')
                date.text = str(val)
                element.append(date)
            elif val is None or val == '' or len(val) == 0:
            #elif val is None or val == '':
                continue
            elif key == 'Department':
                print('Department')
                dep = Department.objects.get(id = val)
                child = dep.xml()
                element.append(child)
                try:
                    vs = VoterService.objects.get(id = dep.VoterService_id)
                    print('VoterService')
                    child.append(vs.xml())
                except:
                    ObjectDoesNotExist
            # elif key == 'VoterService':
            #     print('Voter Service')
            #     vs = VoterService.objects.get(id = val)
            #     child = vs.xml()
            #     element.append(child)
            else:
                #regular value
                child = Element(key)
                child.text = str(val)
                element.append(child)
    return(element)

# Create your models here.

class Source(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    Name = models.CharField(max_length = 500, blank = True, null = True)
    VipId = models.CharField(max_length = 50, blank = True, null = True)
    DateTime = models.CharField(max_length = 50, blank = True, null = True)

class InternationalizedText(models.Model):
    Language = models.CharField(max_length = 2, default = 'en')
    LanguageString = models.CharField(max_length = 5000)

    def __str__(self):
        return("{}: {}".format(self.Language, self.LanguageString))

    def xml(self):
        it_element = Element('Text', attrib = {'language': self.Language})
        it_element.text = self.LanguageString
        return(it_element)

class ExternalIdentifier(models.Model):
    Type = models.CharField(max_length = 50, blank = True, null = True)
    OtherType = models.CharField(max_length = 100, blank = True, null = True)
    Value = models.CharField(max_length = 100, blank = True, null = True)

    def __str__(self):
        return("{}: {}".format(self.Type, self.Value))

    def dict(self):
        return(model_to_dict(self, exclude = ['id']))

    def xml(self):
        element = Element('ExternalIdentifier')
        for key, val in self.dict().items():
            if val is not None:
                child = Element(key)
                child.text = str(val)
                element.append(child)
        return(element)



class Hours(models.Model):
    StartTime = models.CharField(max_length = 50, blank = True, null = True)
    EndTime = models.CharField(max_length = 50, blank = True, null = True)

    def xml(self):
        return(xml_element(self))


class Schedule(models.Model):
    Hours = models.ManyToManyField(Hours, blank = True, max_length = 1000)
    IsOnlyByAppointment = models.CharField(max_length = 50, blank = True, null = True)
    IsOrByAppointment = models.CharField(max_length = 50, blank = True, null = True)
    IsSubjectToChange = models.CharField(max_length = 50, blank = True, null = True)
    StartDate = models.CharField(max_length = 50, blank = True, null = True)
    EndDate = models.CharField(max_length = 50, blank = True, null = True)

    def xml(self):
        schedule = etree.Element('Schedule')
        for key, val in model_to_dict(self, exclude = ['id']).items():
            if isinstance(val, list):
                for ho in val:
                    child = ho.xml()
                    schedule.append(child)
            elif val != None:
                child = Element(key)
                child.text = str(val)
                schedule.append(child)
        return(schedule)

class HoursOpen(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    Schedule = models.ManyToManyField(Schedule, blank = True, max_length = 1000)

    def xml(self):
        hoursopen = etree.Element('HoursOpen', attrib = {'id':self.id})
        for key, val in model_to_dict(self, exclude = ['id']).items():
            if isinstance(val, list):
                for sch in val:
                    child = sch.xml()
                    hoursopen.append(child)
            else:
                child = Element(key)
                child.text = str(val)
                hoursopen.append(child)
        return(hoursopen)

class LatLng(models.Model):
    Latitude = models.CharField(max_length = 50)
    Longitude = models.CharField(max_length = 50)
    Source = models.CharField(max_length = 50, blank = True, null = True)

    def __str__(self):
        return("{}: {}, {}".format(self.Source, self.Latitude, self.Longitude))

    def xml(self):
        sequence = fields_for_model(self, exclude = ['id']).keys()
        dict = model_to_dict(self, exclude = ['id'])
        element = etree.Element('LatLng')
        for key in sequence:
            val = dict[key]
        #for key, val in model_to_dict(self, exclude = ['id']).items():
            #print(key, val)
            if val != None or val != '':
                child = Element(key)
                child.text = str(val)
                element.append(child)
        latlng = model_to_dict(self, exclude = ['id'])
        return(element)



class ContactInformation(models.Model):
    AddressLine = models.CharField(max_length = 1000, blank = True, null = True)
    Directions = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200)
    Email = models.CharField(max_length = 100, blank = True, null = True)
    Fax = models.CharField(max_length = 100, blank = True, null = True)
    HoursOpenId = models.CharField(max_length = 100, blank = True, null = True)
    LatLng = models.CharField(max_length = 100, blank = True, null = True)
    Name = models.CharField(max_length = 1000, blank = True, null = True)
    Phone = models.CharField(max_length = 100, blank = True, null = True)
    Uri = models.URLField(blank = True, null = True)
    parent_id = models.CharField(max_length = 100, blank = True, null = True)

    def dict(self):
        return(model_to_dict(self, exclude = ['id','parent_id']))

    def xml(self):
        element = Element('ContactInformation')
        for key, val in self.dict().items():
            if isinstance(val, list) and len(val) > 0:
                child = Element(key)
                it_child = Element('Text', attrib = {'language': i.Language})
                it_child.text = i.LanguageString
                child.append(it_child)
                element.append(child)
            else:
                if val is None or val == '' or len(val) == 0:
                    continue
                else:
                    child = Element(key)
                    child.text = str(val)
                    element.append(child)
        return(element)



class Party(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    Abbreviation = models.CharField(max_length = 50, blank = True, null = True)
    Color = models.CharField(max_length = 10, blank = True, null = True)
    ExternalIdentifiers = models.ManyToManyField(ExternalIdentifier, blank = True, max_length = 1000)
    IsWriteIn = models.CharField(max_length = 10, blank = True, null = True)
    LogoUri = models.URLField(blank = True, null = True)
    Name = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200)

class Person(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    ContactInformation = models.ManyToManyField(ContactInformation, blank = True, max_length = 1000)
    DateOfBirth = models.DateTimeField(blank = True, null = True)
    ExternalIdentifiers = models.ManyToManyField(ExternalIdentifier, blank = True, max_length = 1000)
    FirstName = models.CharField(max_length = 50, blank = True, null = True)
    FullName = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'person_full_name')
    Gender = models.CharField(max_length = 50, blank = True, null = True)
    LastName = models.CharField(max_length = 50, blank = True, null = True)
    MiddleName = models.CharField(max_length = 50, blank = True, null = True)
    Nickname = models.CharField(max_length = 50, blank = True, null = True)
    PartyId = models.ForeignKey(Party, on_delete = models.CASCADE, db_column = 'PartyId', blank = True, null = True)
    Prefix = models.CharField(max_length = 50, blank = True, null = True)
    Profession = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'person_profession')
    Suffix = models.CharField(max_length = 50, blank = True, null = True)
    Title = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'person_title')


class Candidate(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    BallotName = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200)
    ContactInformation = models.ManyToManyField(ContactInformation, blank = True, max_length = 1000)
    ExternalIdentifiers = models.ManyToManyField(ExternalIdentifier, blank = True, max_length = 1000)
    FileDate = models.CharField(max_length = 50, blank = True, null = True)
    IsIncumbent = models.CharField(max_length = 50, blank = True, null = True)
    IsTopTicket = models.CharField(max_length = 50, blank = True, null = True)
    PartyId = models.ForeignKey(Party, on_delete = models.CASCADE, db_column = 'PartyId', blank = True, null = True)
    PersonId = models.ForeignKey(Person, on_delete = models.CASCADE, db_column = 'PersonId', blank = True, null = True)
    PostElectionStatus = models.CharField(max_length = 50, blank = True, null = True)
    PreElectionStatus = models.CharField(max_length = 50, blank = True, null = True)
    SequenceOrder = models.CharField(max_length = 50, blank = True, null = True)

class BallotMeasureSelection(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    Selection = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200)
    SequenceOrder = models.CharField(max_length = 50, blank = True, null = True)

    def __str__(self):
        return(self.id)

class BallotMeasureContest(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    Abbreviation = models.CharField(max_length = 100, blank = True, null = True)
    BallotSelectionIds = models.ManyToManyField(BallotMeasureSelection, blank = True, max_length = 1000)
    BallotSubTitle = models.ManyToManyField(InternationalizedText, related_name = 'bmc_ballot_sub_title',blank = True, max_length = 200)
    BallotTitle = models.ManyToManyField(InternationalizedText, related_name = 'bmc_ballot_title',blank = True, max_length = 200)
    ElectoralDistrictId = models.ForeignKey('ElectoralDistrict', blank = True, db_column = 'ElectoralDistrictId', on_delete = models.CASCADE)
    ElectorateSpecification = models.ManyToManyField(InternationalizedText, related_name = 'bmc_electorate_specification',blank = True, max_length = 200)
    ExternalIdentifiers = models.ManyToManyField(ExternalIdentifier, blank = True, max_length = 200)
    HasRotation = models.CharField(max_length = 50, blank = True, null = True)
    Name = models.CharField(max_length = 100, blank = True, null = True)
    SequenceOrder = models.CharField(max_length = 100, blank = True, null = True)
    VoteVariation = models.CharField(max_length = 100, blank = True, null = True)
    OtherVoteVariation = models.CharField(max_length = 100, blank = True, null = True)
    ConStatement = models.ManyToManyField(InternationalizedText, related_name = 'bmc_con_statement', blank = True, max_length = 200)
    EffectOfAbstain = models.ManyToManyField(InternationalizedText, related_name = 'bmc_effect_of_abstain',blank = True, max_length = 200)
    FullText = models.ManyToManyField(InternationalizedText, related_name = 'bmc_full_text',blank = True, max_length = 200)
    InfoUri = models.URLField(blank = True, null = True)
    PassageThreshold = models.ManyToManyField(InternationalizedText, related_name = 'bmc_passage_threshold',blank = True, max_length = 200)
    ProStatement = models.ManyToManyField(InternationalizedText, related_name = 'bmc_pro_statement',blank = True, max_length = 200)
    SummaryText = models.ManyToManyField(InternationalizedText, related_name = 'bmc_summary_text',blank = True, max_length = 200)
    Type = models.CharField(max_length = 50, blank = True, null = True)
    OtherType = models.CharField(max_length = 50, blank = True, null = True)

class CandidateSelection(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    SequenceOrder = models.CharField(max_length = 50, blank = True, null = True)
    CandidateIds = models.ManyToManyField(Candidate, blank = True, max_length = 200)
    EndorsementPartyIds = models.ManyToManyField(Party, blank = True, max_length = 200)
    IsWriteIn = models.CharField(max_length = 50, blank = True, null = True)

class CandidateContest(models.Model):
    id = models.CharField(primary_key = True, max_length = 100)
    Abbreviation = models.CharField(max_length = 100, blank = True, null = True)
    BallotSelectionIds = models.ManyToManyField(CandidateSelection, blank = True, max_length = 1000)
    BallotSubTitle = models.ManyToManyField(InternationalizedText, related_name = 'cc_ballot_sub_title',blank = True, max_length = 200)
    BallotTitle = models.ManyToManyField(InternationalizedText, related_name = 'cc_ballot_title',blank = True, max_length = 200)
    ElectoralDistrictId = models.ForeignKey('ElectoralDistrict',on_delete = models.CASCADE, db_column = 'ElectoralDistrictId', max_length = 1000)
    ElectorateSpecification = models.ManyToManyField(InternationalizedText, related_name = 'cc_electorate_specification', blank = True, max_length = 200)
    ExternalIdentifiers = models.ManyToManyField(ExternalIdentifier, blank = True, max_length = 1000)
    HasRotation = models.CharField(max_length = 1000, blank = True, null = True)
    Name = models.CharField(max_length = 2000, blank = True, null = True)
    SequenceOrder = models.CharField(max_length = 100, blank = True, null = True)
    VoteVariation = models.CharField(max_length = 100, blank = True, null = True)
    OtherVoteVariation = models.CharField(max_length = 100, blank = True, null = True)
    NumberElected = models.CharField(max_length = 100, blank = True, null = True)
    OfficeIds = models.ManyToManyField('Office', blank = True, max_length = 1000)
    PrimaryPartyIds = models.ManyToManyField('Party', blank = True, max_length = 1000)
    VotesAllowed = models.CharField(max_length = 100, blank = True, null = True)

class Election(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    Date = models.CharField(max_length = 50, blank = True, null = True)
    HoursOpenId = models.CharField(max_length = 50, blank = True, null = True)
    PollingHours = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'election_hours')
    ElectionType = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'election_type')
    StateId = models.ForeignKey('State', on_delete=models.CASCADE, db_column = 'StateId')
    IsStatewide = models.CharField(max_length = 10, blank = True, null = True)
    Name = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'election_name')
    RegistrationInfo = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'election_registration_info')
    AbsenteeBallotInfo = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'absentee_ballot_info')
    ResultsUri = models.URLField(blank = True, null = True)
    HasElectionDayRegistration = models.CharField(max_length = 10, blank = True, null = True)
    RegistrationDeadline = models.CharField(max_length = 50, blank = True, null = True)
    AbsenteeRequestDeadline = models.CharField(max_length = 50, blank = True, null = True)

class VoterService(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    Description = models.ForeignKey(InternationalizedText, blank = True, max_length = 2000, on_delete = models.CASCADE)
    Type = models.CharField(max_length = 50, blank = True, null = True)

    def dict(self):
        return(model_to_dict(self, exclude = ['id']))

    def xml(self):
        element = etree.Element('VoterService')
        for key, val in self.dict().items():
            if key == 'Description':
                child = Element('Description')
                it = InternationalizedText.objects.get(id = val)
                child.append(it.xml())
            else:
                if val is None or val == '' or len(val) == 0:
                    continue
                else:
                    child = Element(key)
                    child.text = str(val)
                    element.append(child)
        return(element)

class Department(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    ContactInformation = models.ManyToManyField(ContactInformation, blank = True, max_length = 1000)
    ElectionOfficialPersonId = models.ForeignKey(Person, db_column = 'ElectionOfficialPersonId', on_delete = models.CASCADE, blank = True, null = True)
    VoterService = models.ForeignKey(VoterService, on_delete = models.CASCADE, blank = True, null = True)
    election_administration_id = models.CharField(max_length = 50, blank = True, null = True)

    #def __str__(self):
    #    return(self.ContactInformation)

    def dict(self):
        return(model_to_dict(self, exclude = ['id']))

    def xml(self):
        element = etree.Element('Department')
        for key, val in self.dict().items():
            if isinstance(val, list) and len(val) > 0:
                for i in val:
                    child = Element(key)
                    it_child = Element('Text', attrib = {'language': i.Language})
                    it_child.text = i.LanguageString
                    child.append(it_child)
                    element.append(child)
            # elif key == 'VoterService':
            #     print('Voter Service')
            #     vs = VoterService.objects.get(id = val)
            #     child = vs.xml()
            #     element.append(child)
            else:
                if val is None or val == '' or len(val) == 0:
                    continue
                else:
                    child = Element(key)
                    child.text = str(val)
                    element.append(child)
        return(element)

class ElectionNotice(models.Model):
    NoticeText = models.ManyToManyField(InternationalizedText, blank = True, max_length = 5000)
    NoticeUri = models.URLField(blank = True, null = True)

    def dict(self):
        return(model_to_dict(self, exclude = ['id']))

    def xml(self):
        element = Element('ElectionNotice')
        for key, val in self.dict().items():
            if isinstance(val, list) and len(val) > 0:
                for i in val:
                    child = Element(key)
                    it_child = Element('Text', attrib = {'language': i.Language})
                    it_child.text = i.LanguageString
                    child.append(it_child)
                    element.append(child)
            else:
                if val is None or val == '' or len(val) == 0:
                    continue
                else:
                    child = Element(key)
                    child.text = str(val)
                    element.append(child)
        return(element)

class ElectionAdministration(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    AbsenteeUri = models.URLField(blank = True, null = True)
    AmIRegisteredUri = models.URLField(blank = True, null = True)
    BallotTrackingUri = models.URLField(blank = True, null = True)
    BallotProvisionalTrackingUri = models.URLField(blank = True, null = True)
    Department = models.ForeignKey(Department, on_delete = models.CASCADE, max_length = 2000, default = 'dep1')
    ElectionNotice = models.ManyToManyField(ElectionNotice, blank = True, null = True)
    ElectionsUri = models.URLField(max_length = 1000, blank = True, null = True)
    RegistrationUri = models.URLField(blank = True, null = True)
    RulesUri = models.URLField(blank = True, null = True)
    WhatIsOnMyBallotUri = models.URLField(blank = True, null = True)
    WhereDoIVoteUri = models.URLField(blank = True, null = True)

class ElectoralDistrict(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    ExternalIdentifiers = models.ManyToManyField(ExternalIdentifier, blank = True, max_length = 1000)
    Name = models.CharField(blank = True, null = True ,max_length = 100)
    Number = models.CharField(blank = True, null = True ,max_length = 50)
    Type = models.CharField(blank = True, null = True ,max_length = 50)
    OtherType = models.CharField(blank = True, null = True ,max_length = 50)

    def __str__(self):
        return("Name: {}; Number: {}".format(self.Name, self.Number))

class Office(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    ContactInformation = models.ManyToManyField(ContactInformation, blank = True, max_length = 1000)
    Description = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'office_description')
    ElectoralDistrictId = models.ForeignKey(ElectoralDistrict, db_column = 'ElectoralDistrictId', on_delete = models.CASCADE, blank = True, null = True)
    ExternalIdentifiers = models.ManyToManyField(ExternalIdentifier, blank = True, max_length = 1000)
    FilingDeadline = models.CharField(blank = True, null = True, max_length = 100)
    IsPartisan = models.CharField(blank = True, null = True, max_length = 100)
    Name = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'office_name')
    OfficeHolderPersonIds = models.ManyToManyField(Person, blank = True)
    Term = models.CharField(blank = True, null = True, max_length = 100)


class Locality(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    ElectionAdministrationId = models.ForeignKey('ElectionAdministration', on_delete = models.CASCADE, db_column = 'ElectionAdministrationId', blank = True, null = True)
    ExternalIdentifiers = models.ManyToManyField(ExternalIdentifier, blank = True, max_length = 1000)
    IsMailOnly = models.CharField(max_length = 50, blank = True, null = True)
    Name = models.CharField(max_length = 100, blank = False, default = None)
    PollingLocationIds = models.ManyToManyField('PollingLocation',max_length = 10000, blank = True)
    StateId = models.ForeignKey('State', on_delete = models.CASCADE, db_column = 'StateId', blank = True, null = True)
    Type = models.CharField(blank = True, null = True, max_length = 100)
    OtherType = models.CharField(blank = True, null = True, max_length = 100)

    # def __str__(self):
    #     return(self.Name)

class SimpleAddressType(models.Model):
    Line1 = models.CharField(max_length = 100)
    Line2 = models.CharField(blank = True, null = True, max_length = 100, default = '')
    Line3 = models.CharField(blank = True, null = True, max_length = 100, default = '')
    City = models.CharField(max_length = 100)
    State = models.CharField(max_length = 100)
    Zip = models.CharField(blank = True, null = True, max_length = 100, default = "")

    def dict(self):
        dict = model_to_dict(self, exclude = ['id'])
        sequence = fields_for_model(self, exclude = ['id']).keys()
        for i in sequence:
            o_dict = collections.OrderedDict(i = dict[i])
        return(o_dict)
        #return(model_to_dict(self, exclude = ['id']))

    def xml(self):
        element = Element('AddressStructured')
        dict = model_to_dict(self, exclude = ['id'])
        sequence = fields_for_model(self, exclude = ['id']).keys()
        for i in sequence:
            val = dict[i]
            if val is not None:
                child = Element(i)
                child.text = str(val)
                element.append(child)
        return(element)

class PollingLocation(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    AddressStructured = models.ManyToManyField(SimpleAddressType, blank = True, null = True)
    AddressLine = models.CharField(blank = True, null = True, max_length = 1000)
    Directions = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200, related_name = 'pl_directions')
    Hours = models.ManyToManyField(InternationalizedText, blank = True, max_length = 200)
    #HoursOpenId = models.ForeignKey('HoursOpen', on_delete=models.CASCADE, blank = True, null = True)
    HoursOpenId = models.ForeignKey(HoursOpen, db_column = 'HoursOpenId', on_delete = models.SET_NULL, max_length = 50, blank = True, null = True)
    IsDropBox = models.CharField(max_length = 50, blank = True, null = True, default = 'false')
    IsEarlyVoting = models.CharField(max_length = 50, blank = True, null = True, default = 'false')
    LatLng = models.ManyToManyField(LatLng, db_column = 'LatLng', max_length = 50, null = True, blank = True)
    Name = models.CharField(blank = True, null = True, max_length = 1000)
    PhotoUri = models.URLField(blank = True, null = True)

    def __str__(self):
        return(self.Name)

class OrderedContest(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    ContestId = models.ForeignKey(CandidateContest, db_column = 'ContestId', on_delete = models.CASCADE, max_length = 50, blank = True, null = True)
    OrderedBallotSelectionIds = models.ManyToManyField(CandidateSelection, blank = True, max_length = 1000)

class BallotStyle(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    ImageUri = models.URLField(blank = True, null = True)
    OrderedContestIds = models.ManyToManyField(OrderedContest, blank = True, max_length = 1000)
    PartyIds = models.ManyToManyField(Party, blank = True, max_length = 1000)

class Precinct(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    BallotStyleId = models.ForeignKey(BallotStyle, db_column = 'BallotStyleId', on_delete = models.CASCADE, max_length = 50, blank = True, null = True)
    ElectoralDistrictIds = models.ManyToManyField(ElectoralDistrict, max_length = 1000, blank = True)
    ExternalIdentifiers = models.ManyToManyField(ExternalIdentifier, blank = True, max_length = 1000)
    IsMailOnly = models.CharField(max_length = 50, blank = True, null = True)
    LocalityId = models.ForeignKey(Locality, db_column = 'LocalityId', on_delete = models.CASCADE, max_length = 50)
    Name = models.CharField(max_length = 200, blank = True, null = True)
    Number = models.CharField(max_length = 50, blank = True, null = True)
    PollingLocationIds = models.ManyToManyField(PollingLocation,max_length = 1000, blank = True)
    PrecinctSplitName = models.CharField(max_length = 50, blank = True, null = True)
    Ward = models.CharField(max_length = 50, blank = True, null = True)

    def __str__(self):
        return("{} ({})".format(self.Name, self.LocalityId.Name))

class State(models.Model):
    id = models.CharField(primary_key = True, max_length = 50, default = "st1")
    ElectionAdministrationId = models.ForeignKey(ElectionAdministration, on_delete = models.CASCADE, db_column = 'ElectionAdministrationId', blank = True, null = True)
    ExternalIdentifiers = models.ManyToManyField(ExternalIdentifier, blank = True, max_length = 1000)
    Name = models.CharField(max_length = 50, blank = True, null = True)
    PollingLocationIds = models.ManyToManyField(PollingLocation, max_length = 1000, blank = True)

    def __str__(self):
        return(self.Name)

    def dict(self):
        return(model_to_dict(self, exclude = ['id']))


class StreetSegment(models.Model):
    id = models.CharField(primary_key = True, max_length = 50)
    AddressDirection = models.CharField(max_length = 50, blank = True, null = True)
    City = models.CharField(max_length = 50, blank = True, null = True)
    IncludesAllAddresses = models.CharField(max_length = 50, blank = True, null = True)
    IncludesAllStreets = models.CharField(max_length = 50, blank = True, null = True)
    OddEvenBoth = models.CharField(max_length = 50, blank = True, null = True)
    PrecinctId = models.ForeignKey(Precinct, on_delete = models.CASCADE, db_column = 'PrecinctId')
    StartHouseNumber = models.CharField(max_length = 50, blank = True, null = True)
    EndHouseNumber = models.CharField(max_length = 50, blank = True, null = True)
    HouseNumberPrefix = models.CharField(max_length = 50, blank = True, null = True)
    HouseNumberSuffix = models.CharField(max_length = 50, blank = True, null = True)
    State = models.CharField(max_length = 50, blank = True, null = True)
    StreetDirection = models.CharField(max_length = 50, blank = True, null = True)
    StreetName = models.CharField(max_length = 50, blank = True, null = True)
    StreetSuffix = models.CharField(max_length = 50, blank = True, null = True)
    UnitNumber = models.CharField(max_length = 500, blank = True, null = True)
    Zip = models.CharField(max_length = 50, blank = True, null = True)

class Error(models.Model):
    id_error = models.CharField(max_length = 50, blank = True, null = True)
    error_object = models.CharField(max_length = 50, blank = True, null = True)
    error_message = models.CharField(max_length = 500, blank = True, null = True)
