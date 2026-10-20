package com.querypilot.metadata;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Collection;
import java.util.List;

public interface SchemaColumnRepository extends JpaRepository<SchemaColumn, Long> {

    List<SchemaColumn> findByTableIdInOrderByIdAsc(Collection<Long> tableIds);
}
