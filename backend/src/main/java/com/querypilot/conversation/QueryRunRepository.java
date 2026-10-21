package com.querypilot.conversation;

import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface QueryRunRepository extends JpaRepository<QueryRun, Long> {

    List<QueryRun> findAllByOrderByIdDesc();
}
