"""
.. module:: artist_ipi

The **Artist IPI** Model. Holds the Interested Parties Information code. The
IPI is an 11-digit number.

    See the `IPI Documentation on MusicBrainz`_.
    See the `IPI Wikipedia page`_.

.. _IPI Documentation on MusicBrainz: https://musicbrainz.org/doc/IPI
.. _IPI Wikipedia page: https://en.wikipedia.org/wiki/Interested_Parties_Information

PostgreSQL Definition
---------------------

The :code:`artist_ipi` table is defined in the MusicBrainz Server as:

.. code-block:: sql

    CREATE TABLE artist_ipi ( -- replicate (verbose)
        artist              INTEGER NOT NULL, -- PK, references artist.id
        ipi                 CHAR(11) NOT NULL CHECK (ipi ~ E'^\\d{11}$'), -- PK
        edits_pending       INTEGER NOT NULL DEFAULT 0 CHECK (edits_pending >= 0),
        created             TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );

"""

from django.db import models
from django.core.validators import MinLengthValidator
from django.core.validators import RegexValidator


def validate_artist_ipi(sender, instance, **kwargs):
    import re
    if not re.match(sender.IPI_REGEX, instance.ipi):
        from django.core.exceptions import ValidationError
        raise ValidationError(RegexValidator.message)
    

class artist_ipi(models.Model):
    """ 
    Not all parameters are listed here, only those that present some interest
    in their Django implementation.

    :param artist: This field is interesting because it is both a Foreign Key
        to the Artist model, as well the Primary Key for the Artist IPI
        model. In Django, this can be implemented as a `OneToOneField`.
    :param str ipi: Both the `artist` and the `ipi` fields are primary keys
        in the SQL. In Django, there can only be 1 primary key per model.
        Therefore, the uniqueness required for a primary key is defined in
        this Django model field with a `unique` flag. Furthermore, there is a
        regex-based check in SQL. In Django, this can be implemented with a
        `RegexValidator`, but that is only applied in the frontend. For
        backend validation, a `pre_save` signal is used.
    :param int edits_pending: the MusicBrainz Server uses a PostgreSQL `check`
        to validate that the value is a positive integer. In Django, this is
        done with `models.PositiveIntegerField()`.    
    """

    IPI_REGEX = r'^\d{11}$'

    artist = models.OneToOneField('artist', primary_key=True)
    ipi = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            MinLengthValidator(11),
            RegexValidator(regex=IPI_REGEX)            
        ]
    )
    edits_pending = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.ipi

    def __str__(self):
        return self.ipi

    class Meta:
        db_table = 'artist_ipi'


models.signals.pre_save.connect(validate_artist_ipi, sender=artist_ipi)
