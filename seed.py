from models import Challenge, db, Requirement
from app import app
with app.app_context():
    db.drop_all()
    db.create_all()

    c1 = Challenge(challenge_start="2022-11-30 00:00:00.061592-08", challenge_end="2022-12-07 00:00:00.061592-08", name="Tidecaller")
    db.session.add(c1)
    db.session.commit()

    r1 = Requirement(card_code="05BW003", card_quantity="3", challenge_id=c1.id)
    r2 = Requirement(card_code="06BW014", card_quantity="3", challenge_id=c1.id)
    db.session.add(r1)
    db.session.add(r2)
    db.session.commit()

    c2 = Challenge(challenge_start="2022-12-7 00:00:00.061592-08", challenge_end="2022-12-14 00:00:00.061592-08", name="Cosmic Empyrean")
    db.session.add(c2)
    db.session.commit()

    r3 = Requirement(card_code="06IO016", card_quantity="3", challenge_id=c2.id)
    r4 = Requirement(card_code="03MT035", card_quantity="3", challenge_id=c2.id)
    db.session.add(r3)
    db.session.add(r4)
    db.session.commit()

    c3 = Challenge(challenge_start="2022-12-14 00:00:00.061592-08", challenge_end="2022-12-21 00:00:00.061592-08", name="Volatile Studies")
    db.session.add(c3)
    db.session.commit()

    r6 = Requirement(card_code="04SH067", card_quantity="3", challenge_id=c3.id)
    r5 = Requirement(card_code="04SH011", card_quantity="3", challenge_id=c3.id)
    db.session.add(r5)
    db.session.add(r6)
    db.session.commit()