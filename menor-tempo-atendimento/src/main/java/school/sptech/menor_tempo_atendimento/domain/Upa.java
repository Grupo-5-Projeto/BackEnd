package school.sptech.menor_tempo_atendimento.domain;


import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import org.springframework.stereotype.Service;
import school.sptech.menor_tempo_atendimento.Nivel;

@Entity
public class Upa {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id_upa;
    private String nome;
    @Column(name = "tempo_espera")
    private Integer tempoDeEspera;
    @Transient
    private Nivel nivel;

    public Upa(String nome, Integer tempoDeEspera) {
        this.nome = nome;
        tempoDeEspera = tempoDeEspera;
        this.nivel = Nivel.NIVEL_MEIO_DE_TRANSPORTE;
    }

    public Upa() {
    }

    public Integer getId_upa() {
        return id_upa;
    }

    public void setId_upa(Integer id_upa) {
        this.id_upa = id_upa;
    }

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public Integer getTempoDeEspera() {
        return tempoDeEspera;
    }

    public void setTempoDeEspera(Integer tempoDeEspera) {
        this.tempoDeEspera = tempoDeEspera;
    }

    public Nivel getNivel() {
        return nivel;
    }

    public void setNivel(Nivel nivel) {
        this.nivel = nivel;
    }
}
