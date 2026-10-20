package com.querypilot.metadata;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface BusinessMetricRepository extends JpaRepository<BusinessMetric, Long> {

    List<BusinessMetric> findByDatasetIdOrderByIdAsc(Long datasetId);
}
