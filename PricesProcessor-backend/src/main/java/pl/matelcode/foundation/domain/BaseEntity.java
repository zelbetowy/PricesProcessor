package pl.matelcode.foundation.domain;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;
import lombok.Data;

import java.time.LocalDateTime;


@NoArgsConstructor
@AllArgsConstructor
@MappedSuperclass
@Data
public class BaseEntity {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  @CreationTimestamp
  @Column(name = "created_at", updatable = false)
  private LocalDateTime createdAt;


  @UpdateTimestamp
  @Column(name = "updated_at")
  private LocalDateTime updatedAt;

}
