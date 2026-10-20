package com.querypilot.metadata;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface SchemaTableRepository extends JpaRepository<SchemaTable, Long> {

    List<SchemaTable> findByDatasetIdOrderByIdAsc(Long datasetId);

    List<SchemaTable> findByDatasetIdAndAccessibleTrueOrderByIdAsc(Long datasetId);
}
