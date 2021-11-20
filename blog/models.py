from django.conf import settings
from django.db import models
from django.utils import timezone


class Well(models.Model):
    serial = models.CharField(max_length=10)
    type = models.CharField(max_length=15)
    created_date = models.DateField(default=timezone.now)
    locate = models.CharField(max_length=30)
    comment = models.CharField(max_length=100)
    req_num = models.CharField(max_length=10)
    trans_date = models.CharField(max_length=15)

    def release(self):
        self.save()

    def __str__(self):
        return self.serial


class WellType(models.Model):
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.id}'


class Warehouse(models.Model):
    wh_name = models.CharField(max_length=25)

    def __str__(self):
        return self.wh_name


class var(models.Model):
    year = models.CharField(max_length=4)
    month = models.CharField(max_length=2)
    part_num = models.CharField(max_length=3)

    def __str__(self):
        return self.year + ' | ' + self.month + ' | ' + self.part_num

class ProjectGroup(models.Model):
    pg_name = models.CharField(max_length=20)

    def addPg(self):
        self.save()

    def __str__(self):
        return f'{self.id}'

class Code(models.Model):
    code_name = models.CharField(max_length=20)
    connect = models.ForeignKey(ProjectGroup, on_delete=models.CASCADE)

    def addCode(self):
        self.save()

    def __str__(self):
        return f'{self.id}'

class Appl_mpz(models.Model):
    mpz_appl_name = models.CharField(max_length=20)
    connect = models.ForeignKey(Code, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}'

class Appl_mpz_data(models.Model):
    applID = models.ForeignKey(Appl_mpz, on_delete=models.CASCADE)
    typeID = models.ForeignKey(WellType, on_delete=models.CASCADE)
    w_value = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.id}'

class Byer(models.Model):
    by_name = models.CharField(max_length=20)

    def addBy(self):
        self.save()

    def __str__(self):
        return f'{self.id}'

class Appl_byer(models.Model):
    by_appl_name = models.CharField(max_length=20)
    connect = models.ForeignKey(Byer, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.id}'

class Appl_by_data(models.Model):
    applID = models.ForeignKey(Appl_byer, on_delete=models.CASCADE)
    byID = models.ForeignKey(Byer, on_delete=models.CASCADE)
    typeID = models.ForeignKey(WellType, on_delete=models.CASCADE)
    w_value = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.id}'







