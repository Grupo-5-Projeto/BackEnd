package school.sptech.menor_tempo_atendimento.repository;



import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import school.sptech.menor_tempo_atendimento.domain.Upa;

import java.util.List;

@Repository
public interface UpaRepository extends JpaRepository<Upa, Integer> {

    @Query(nativeQuery = true, value =
            "SELECT te.tempo_espera, u.id_upa, u.nome " +
            "FROM tempo_espera te " +
            "JOIN upa u ON te.fk_upa = u.id_upa " +
            "WHERE u.nome IN (:nomes);")
    List<Upa> findByNomeIn(List<String> nomes);

    // Método para simular o retorno de dados
//    public List<Upa> getUpas() {
//        return List.of(
//                new Upa("UPA MASATAKA OTA", 5),
//                new Upa("UPA 26 DE AGOSTO", 10),
//                new Upa("UPA CIDADE TIRADENTES", 15)
//        );
//    }
}
