package school.sptech.menor_tempo_atendimento;

import java.util.Objects;

public class NoGrafo {
    private String nome;
    private Nivel nivel;
    private Integer tempo;

    public NoGrafo(String nome, Nivel nivel, Integer tempo) {
        this.nome = nome;
        this.nivel = nivel;
        this.tempo = tempo;
    }

    public NoGrafo() {}

    //    @Override
//    public boolean equals(Object obj) {
//        if (this == obj) return true;
//        if (!(obj instanceof Grafo.NoGrafo)) return false;
//        Grafo.NoGrafo outro = (Grafo.NoGrafo) obj;
//        return Objects.equals(this.nome, outro.nome);
//    }

//    @Override
//    public int hashCode() {
//        return Objects.hash(nome);
//    }

    @Override
    public String toString() {
        return nome;
    }

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public Nivel getNivel() {
        return nivel;
    }

    public void setNivel(Nivel nivel) {
        this.nivel = nivel;
    }
    public Integer getTempo() {
        return tempo;
    }
    public void setTempo(Integer tempo) {
        this.tempo = tempo;
    }
}
