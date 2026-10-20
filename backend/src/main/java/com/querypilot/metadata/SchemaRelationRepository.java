package com.querypilot.metadata;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface SchemaRelationRepository extends JpaRepository<SchemaRelation, Long> {

    List<SchemaRelation> findByDatasetIdOrderByIdAsc(Long datasetId);
}
