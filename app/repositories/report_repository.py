def create_report(
    self, db: Session, *, image_path: str, damage_category: str,
    latitude: float | None, longitude: float | None, reported_by_id: int | None = None
) -> Report:
    db_obj = Report(
        image_path=image_path,
        damage_category=damage_category,
        latitude=latitude,
        longitude=longitude,
        reported_by_id=reported_by_id
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_filtered(self, db: Session, *, damage_type=None, severity=None, owner_id: int | None = None):
    query = db.query(self.model)
    if damage_type:
        query = query.filter(self.model.damage_category.ilike(f"%{damage_type}%"))
    if severity:
        query = query.filter(self.model.severity_level.ilike(severity))
    # owner_id=None means "no restriction" (admin view)
    if owner_id is not None:
        query = query.filter(self.model.reported_by_id == owner_id)
    return query.order_by(self.model.id.desc()).all()