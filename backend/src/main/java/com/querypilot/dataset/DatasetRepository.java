package com.querypilot.dataset;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

public interface DatasetRepository extends JpaRepository<Dataset, Long> {

    @Query("select d from Dataset d join fetch d.source order by d.id")
    List<Dataset> findAllWithSource();
}
