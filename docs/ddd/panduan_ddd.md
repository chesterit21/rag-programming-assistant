# Panduan Komprehensif Domain-Driven Design dalam ASP.NET Core: Pola, Integrasi, dan Praktik Terbaik untuk Aplikasi Skalabel

## 1.Panduan Komprehensif Domain-Driven Design dalam ASP.NET Core: Pola, Integrasi, dan Praktik Terbaik untuk Aplikasi Skalabel


### 1. Pendahuluan Domain-Driven Design (DDD)

Domain-Driven Design (DDD) adalah pendekatan utama dalam desain perangkat lunak yang memfokuskan pemodelan perangkat lunak agar sesuai dengan domain bisnis tertentu, berdasarkan masukan dari para ahli domain. Ini adalah filosofi pengembangan perangkat lunak yang menempatkan domain bisnis yang kompleks sebagai inti dari desain dan implementasi aplikasi.1 Tujuannya adalah untuk menciptakan perangkat lunak yang secara akurat mencerminkan realitas bisnis, mengurangi kesenjangan antara pemahaman teknis dan domain.
Pendekatan ini menekankan penempatan fokus utama proyek pada domain inti dan lapisan logika domain.1 Desain yang kompleks dibangun di atas model domain yang kaya, yang merupakan sistem abstraksi yang menjelaskan aspek-aspek terpilih dari domain dan dapat digunakan untuk memecahkan masalah terkait domain tersebut.1 DDD juga mendorong kolaborasi kreatif dan iteratif antara ahli teknis dan ahli domain untuk menyempurnakan model konseptual yang mengatasi masalah domain tertentu.1 Struktur dan bahasa kode perangkat lunak—seperti nama kelas, metode, dan variabel—seharusnya cocok dengan domain bisnis, memastikan bahwa kode secara intrinsik selaras dengan proses dan konsep bisnis.1

Konsep Inti DDD: Ubiquitous Language dan Bounded Contexts

Dua konsep fundamental yang mendasari DDD adalah Ubiquitous Language dan Bounded Contexts, yang bersama-sama membentuk kerangka kerja untuk mengelola kompleksitas dalam sistem yang besar.

Ubiquitous Language (UL)

Ubiquitous Language adalah bahasa umum yang digunakan dan dipahami oleh semua pemangku kepentingan dalam proyek—baik pengembang maupun ahli domain.2 Bahasa ini digunakan secara konsisten dalam desain dan implementasi perangkat lunak, memastikan bahwa perangkat lunak secara akurat mencerminkan domain bisnis yang dilayaninya.2 Ini berfungsi sebagai "kamus tim" untuk proyek, secara signifikan mengurangi kebingungan dan kebutuhan akan terjemahan mental antara tim atau sub-domain yang berbeda.4
Penggunaan Ubiquitous Language yang konsisten melampaui sekadar komunikasi; ini adalah prinsip desain yang fundamental. Tindakan mendefinisikan dan menegakkan bahasa bersama ini memaksa tingkat presisi dan pemahaman bersama yang secara langsung menghasilkan kode yang lebih baik dan lebih ekspresif. Bahasa ini menjadi cetak biru untuk model domain, membuat kode menjadi dokumentasi diri dan secara intrinsik selaras dengan logika bisnis. Presisi ini sangat penting untuk alat berbasis AI, karena terminologi yang konsisten membantu dalam pengenalan pola dan pemahaman kode. Ubiquitous Language bukan hanya alat komunikasi; ini adalah batasan desain yang memandu struktur perangkat lunak itu sendiri.3 Misalnya, dalam aplikasi perbankan, alih-alih
processTransaction(), bisa ada metode BuchungVornehmen() pada kelas Girokonto.6 Noun dalam bahasa ini sering kali menjadi Entitas atau Objek Nilai, sementara Verb menjadi Metode atau Fungsi yang beroperasi pada objek-objek tersebut.4 Keselarasan yang kuat ini mengurangi technical debt dan meningkatkan pemeliharaan karena perubahan dalam domain dapat dipetakan dengan lebih mudah dalam kode.3

Bounded Contexts (BCs)

DDD menentang gagasan memiliki satu model terpadu untuk seluruh sistem; sebaliknya, sistem besar dibagi menjadi Bounded Contexts, yang masing-masing memiliki model domain dan Ubiquitous Language sendiri.1 Bounded Contexts adalah batasan eksplisit di sekitar sub-domain tertentu, seperti "Manajemen Pesanan" versus "Dukungan Pelanggan".3
Manfaat utama dari Bounded Contexts adalah kemampuannya untuk mengisolasi perubahan, mengurangi coupling, dan memungkinkan tim untuk bekerja secara otonom.3 Isolasi ini mendorong modularitas, meningkatkan pemeliharaan, dan mengakomodasi evolusi domain yang berbeda secara independen.3 Konsep Bounded Contexts adalah pendahulu strategis untuk arsitektur microservices. Dengan secara eksplisit mendefinisikan batasan di mana konsep domain mungkin memiliki arti atau aturan yang berbeda, DDD secara inheren memandu dekomposisi aplikasi monolitik menjadi layanan yang lebih kecil dan dapat di-deploy secara independen.7 Ini bukan hanya tentang mengatur kode; ini tentang mengatur tim dan deployment di sekitar kapabilitas bisnis yang berbeda. Analogi "rumah boneka" menggambarkan isolasi ini dengan sempurna, yang merupakan fundamental untuk menskalakan upaya pengembangan dan mendeploy bagian-bagian sistem secara otonom.9 Ketika batasan dilintasi, makna suatu kata dalam bahasa mungkin berubah, seperti "Pesanan" dalam konteks penjualan yang berbeda dari "Slip Pengepakan" dalam konteks gudang.9 Dekomposisi strategis ini secara langsung mendukung skalabilitas dan meletakkan dasar untuk integrasi kompleks seperti Event-Driven Architecture antar konteks.

Blok Bangunan Taktis DDD: Entitas, Objek Nilai, Agregat, Layanan Domain, Peristiwa Domain

Setelah mendefinisikan batasan strategis, DDD menggunakan blok bangunan taktis untuk mengimplementasikan model domain yang kaya di dalam setiap Bounded Context.
Entitas: Entitas adalah objek yang didefinisikan bukan oleh atributnya, tetapi oleh identitas uniknya yang bertahan sepanjang waktu, terlepas dari perubahan keadaan atau atributnya.1 Kesetaraan entitas ditentukan oleh identitasnya, bukan nilai atributnya.11 Entitas biasanya memiliki siklus hidup yang lebih panjang dan keadaan yang dapat berubah.11 Contoh umum termasuk
Pelanggan atau Pesanan, yang masing-masing memiliki ID unik.11 Entitas harus merangkum perilaku dan aturan domain, mengontrol invarian dan validasi saat mengakses koleksi apa pun.12 Kelas dasar
Entity sering kali menyediakan pengidentifikasi unik, penanganan peristiwa domain, pemeriksaan transien, serta mekanisme kesetaraan dan kode hash.11
Objek Nilai (Value Objects - VOs): Berbeda dengan entitas, Objek Nilai adalah objek yang semata-mata diidentifikasi oleh nilai atributnya; mereka tidak memiliki identitas yang berbeda.2 Objek Nilai secara inheren tidak dapat diubah (immutable), artinya keadaannya tidak berubah setelah dibuat.11 Setiap "modifikasi" pada Objek Nilai sebenarnya mengembalikan instance baru.11 Kesetaraan ditentukan dengan membandingkan semua nilai atributnya.11 Objek Nilai memiliki siklus hidup yang terbatas, sering kali terlingkup pada siklus hidup entitas atau transaksi.11 Mereka digunakan untuk konsep domain yang tidak memerlukan identitas yang berbeda, seperti
Alamat, Uang, Warna, atau Gaji.3 Objek Nilai harus meng-override operator kesetaraan (
== dan !=) serta metode Equals() dan GetHashCode() untuk kesetaraan berbasis nilai.11
Agregat: Agregat adalah kumpulan objek domain (entitas dan objek nilai) yang diperlakukan sebagai satu unit untuk tujuan konsistensi transaksional.2 Agregat bertanggung jawab untuk menegakkan aturan bisnis invarian yang harus selalu berlaku untuk kelompok tersebut.13
Aggregate Root (AR): Setiap agregat memiliki satu entitas pusat yang disebut Aggregate Root. AR adalah satu-satunya titik akses untuk semua interaksi dengan agregat dari luar.6 Semua perubahan pada entitas di dalam agregat harus melalui AR untuk memastikan invarian ditegakkan.13 Ketergantungan antara entitas di dalam agregat dan objek di luar agregat harus dihindari.13 Contoh klasik adalah
Pesanan (AR) dan ItemPesanan-nya (entitas di dalam agregat).3 AR sering kali memiliki setter privat untuk koleksi internal dan mengekspos koleksi read-only (
IReadOnlyCollection<T>) untuk mencegah perubahan arbitrer dari luar.12 Konstruktor publik untuk AR memastikan konsistensi awal, sementara konstruktor internal untuk entitas anak membatasi pembuatan di dalam assembly domain.13 Agregat bukan hanya mekanisme pengelompokan; ini adalah batasan transaksional yang menjamin integritas data dalam operasi bisnis tertentu. Dengan memaksa semua interaksi eksternal melalui Aggregate Root, DDD memastikan bahwa aturan bisnis kompleks (invarian) selalu diterapkan secara konsisten, mencegah sistem memasuki keadaan tidak valid. Ini adalah keberangkatan penting dari model CRUD tradisional di mana logika bisnis mungkin tersebar atau diterapkan secara tidak konsisten. Penegakan invarian yang ketat pada batas agregat ini merupakan fundamental untuk membangun sistem yang kuat dan skalabel, terutama ketika mempertimbangkan transaksi terdistribusi atau skenario konsistensi eventual. Jika agregat dirancang dengan benar, kompleksitas pengelolaan konsistensi pada tingkat yang lebih tinggi (misalnya, di seluruh microservices) berkurang secara signifikan karena setiap agregat secara internal konsisten. Ini berarti bahwa desain agregat secara langsung memengaruhi keandalan dan kesederhanaan pengelolaan konsistensi dalam sistem yang lebih besar.
Layanan Domain (Domain Services): Layanan Domain adalah kelas tanpa status yang berisi logika domain inti yang tidak secara alami sesuai dengan satu entitas atau agregat tunggal.3 Layanan ini digunakan ketika logika bergantung pada layanan eksternal (seperti repositori) atau melibatkan lebih dari satu agregat/entitas.16 Mereka biasanya dinamai dengan sufiks
Manager atau Service (misalnya, OrderService, IssueManager).3 Layanan Domain beroperasi pada objek domain (entitas, objek nilai), bukan DTO 16, dan biasanya digunakan oleh Layanan Aplikasi atau Layanan Domain lainnya.16
Peristiwa Domain (Domain Events): Peristiwa Domain adalah sinyal bahwa sesuatu yang signifikan telah terjadi dalam domain.3 Mereka memungkinkan komunikasi yang efektif antara berbagai komponen aplikasi, meningkatkan fleksibilitas dan skalabilitas melalui decoupling.17 Peristiwa Domain membantu memisahkan logika bisnis inti dari proses sekunder (misalnya, mengirim notifikasi atau logging).17 Mereka dapat ditangani secara asinkron untuk skalabilitas dan pengelolaan beban yang lebih baik.17 Peristiwa Domain sangat selaras dengan prinsip-prinsip DDD, memungkinkan pemodelan perilaku aplikasi dalam hal konsep dan tindakan domain.17 Implementasinya melibatkan pendefinisian jenis peristiwa (kelas data sederhana), pemicuan peristiwa di dalam entitas/layanan, dan berlangganan peristiwa ini di handler.17 Pustaka seperti MediatR dapat menyederhanakan proses ini.17 Peristiwa Domain adalah sistem perpesanan internal dari suatu bounded context, memungkinkan komponen dalam konteks tersebut untuk bereaksi terhadap kejadian domain yang signifikan tanpa coupling langsung. Pendekatan "reaktif" ini berarti bahwa alih-alih meng-coupling komponen secara erat (misalnya,
OrderService secara langsung memanggil EmailService), agregat Order cukup memublikasikan OrderCompletedEvent. Sejumlah handler kemudian dapat berlangganan peristiwa ini, memungkinkan fungsionalitas baru (seperti mengirim email, memperbarui poin loyalitas, atau logging) ditambahkan tanpa memodifikasi logika domain inti. Ini adalah mekanisme yang kuat untuk mencapai kohesi tinggi dan coupling rendah di dalam satu bounded context. Meskipun Peristiwa Domain bersifat internal, mereka adalah jembatan konseptual menuju Peristiwa Integrasi (dibahas nanti). Penerapan peristiwa domain internal yang berhasil membangun fondasi untuk memahami cara berkomunikasi antara bounded context yang berbeda, di mana konsep "peristiwa" meluas ke komunikasi lintas sistem. Pola ini secara langsung mendukung evolusi menuju arsitektur yang lebih kompleks dan terdistribusi seperti Event-Driven Architecture, dengan menetapkan paradigma komunikasi berbasis peristiwa yang jelas pada tingkat taktis. Kemampuan untuk menangani peristiwa secara asinkron adalah pendorong utama untuk kinerja dan skalabilitas, memungkinkan transaksi utama selesai dengan cepat sementara efek samping diproses di latar belakang.

Tabel: Blok Bangunan Inti DDD

Pola/Konsep
Tujuan/Definisi
Karakteristik Kunci
Kapan Digunakan
Contoh C#
Entitas
Objek dengan identitas unik yang bertahan sepanjang waktu, terlepas dari perubahan atribut.
Memiliki identitas (ID), dapat berubah (mutable), siklus hidup panjang, kesetaraan berdasarkan ID.
Untuk objek yang perlu dilacak secara individual sepanjang waktu (misalnya, Pelanggan, Produk, Pesanan).
public class Order : Entity<Guid> { public string OrderNumber { get; private set; } }
Objek Nilai
Objek yang diidentifikasi semata-mata oleh nilai atributnya; tidak memiliki identitas yang berbeda.
Tidak memiliki identitas, tidak dapat diubah (immutable), siklus hidup terbatas, kesetaraan berdasarkan nilai semua atribut.
Untuk konsep yang menggambarkan sesuatu tanpa identitas unik (misalnya, Alamat, Uang, Warna, RentangTanggal).
public class Money : ValueObject { public decimal Amount { get; } public string Currency { get; } }
Agregat & Aggregate Root
Kumpulan objek domain yang diperlakukan sebagai satu unit untuk konsistensi transaksional. Aggregate Root adalah entitas pusat yang mengontrol akses dan menegakkan invarian.
Batasan konsistensi transaksional, AR sebagai titik masuk tunggal, AR menegakkan invarian, kohesi tinggi di dalam, coupling rendah di luar.
Untuk mengelompokkan entitas dan objek nilai yang terkait erat yang harus selalu konsisten bersama (misalnya, Pesanan dan ItemPesanan-nya, AkunBank dan Transaksi-nya).
public class Order : AggregateRoot<Guid> { private List<OrderItem> _items; public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly(); public void AddItem(...) { /* enforce invariants */ } }
Layanan Domain
Kelas tanpa status yang merangkum logika domain yang tidak secara alami sesuai dengan satu entitas atau agregat tunggal.
Tanpa status, beroperasi pada beberapa agregat/entitas, dapat bergantung pada repositori atau layanan eksternal.
Untuk logika bisnis yang melibatkan beberapa agregat atau memerlukan koordinasi dengan layanan eksternal (misalnya, OrderPlacementService, TransferDanaService).
public class OrderPlacementService { public async Task PlaceOrder(...) { /* logic across Order and Product aggregates */ } }
Peristiwa Domain
Sinyal bahwa sesuatu yang signifikan telah terjadi dalam domain. Digunakan untuk mendekopel logika bisnis inti dari efek samping.
Mewakili fakta masa lalu, tidak dapat diubah, internal untuk Bounded Context, dapat diproses secara sinkron atau asinkron.
Untuk mengomunikasikan perubahan keadaan penting dalam domain dan memicu efek samping yang didekopel (misalnya, OrderCreatedEvent, ProductPriceUpdatedEvent).
public record OrderCreatedEvent(Guid OrderId) : IDomainEvent;


### 2. Praktik Terbaik Implementasi DDD dalam ASP.NET Core MVC/Web API

Mengimplementasikan Domain-Driven Design dalam aplikasi ASP.NET Core memerlukan struktur proyek yang terorganisir dengan baik yang mencerminkan prinsip-prinsip DDD, terutama pemisahan kekhawatiran dan aliran dependensi.

Struktur Proyek ASP.NET Core yang Selaras dengan DDD

DDD menekankan pengelompokan fitur secara vertikal berdasarkan domain, yang berarti semua fitur yang terkait dengan domain Pengguna akan ditempatkan di bawah folder atau proyek Pengguna, bahkan jika mereka mengambil data dari sumber database yang sama.15 Pendekatan ini mungkin mengarah pada duplikasi kode, tetapi duplikasi dalam batas tertentu dapat diterima jika itu mendukung isolasi domain.15
Struktur umum yang sering digunakan dengan DDD adalah Clean Architecture (juga dikenal sebagai Onion Architecture, Hexagonal Architecture, atau Ports-and-Adapters).19 Arsitektur ini mengatur kode menjadi lapisan konsentris dengan dependensi yang selalu mengarah ke dalam.19
Lapisan Domain (Core): Ini adalah lapisan terdalam dan inti dari aplikasi.19 Lapisan ini berisi logika bisnis murni, termasuk entitas, objek nilai, agregat, peristiwa domain, layanan domain, antarmuka (untuk repositori, dll.), spesifikasi, dan enum.3 Lapisan Domain harus mandiri dan memiliki sedikit ketergantungan eksternal, terutama hanya pada tipe primitif.NET CLR.19 Ini berfokus pada logika perusahaan dan aturan bisnis yang tidak terpengaruh oleh bagaimana data disimpan atau disajikan.22
Lapisan Aplikasi: Lapisan ini berada tepat di luar Lapisan Domain dan berisi logika bisnis spesifik aplikasi atau kasus penggunaan.3 Ini mengorkestrasi aliran data dan menerapkan aturan bisnis menggunakan entitas dan spesifikasi yang ditentukan dalam Lapisan Domain.22 Lapisan Aplikasi mendefinisikan
apa yang dilakukan aplikasi (misalnya, perintah, kueri, DTO, handler), tetapi tidak bagaimana itu dilakukan (misalnya, bagaimana data disimpan).19 Lapisan ini bergantung pada Lapisan Domain.20
Lapisan Infrastruktur: Lapisan ini bertanggung jawab untuk detail teknis dan ketergantungan eksternal.3 Ini mengimplementasikan antarmuka yang ditentukan di Lapisan Domain atau Aplikasi. Contohnya termasuk implementasi Entity Framework Core untuk persistensi data, klien API eksternal, penyedia email, sistem file, dan implementasi repositori konkret.3 Lapisan Infrastruktur bergantung pada Lapisan Domain dan Aplikasi.22
Lapisan Presentasi (ASP.NET Core Web API/MVC): Ini adalah lapisan terluar dan titik masuk aplikasi.3 Lapisan ini menangani permintaan UI atau API, pemetaan DTO, pengontrol, dan konfigurasi injeksi dependensi.3 Lapisan ini bergantung pada Lapisan Aplikasi.22
Aturan dependensi dalam Clean Architecture menyatakan bahwa dependensi selalu mengalir ke dalam: Lapisan Presentasi bergantung pada Lapisan Aplikasi, yang bergantung pada Lapisan Domain. Lapisan Infrastruktur mengimplementasikan antarmuka yang didefinisikan di Lapisan Domain/Aplikasi tetapi secara fisik berada di luar inti.20 Ini memastikan logika bisnis inti tetap terisolasi dan independen dari detail eksternal.21

Contoh Kode Praktis


Mengimplementasikan Entitas dengan Identitas dan Perilaku

Entitas dalam DDD memiliki identitas unik (misalnya, properti Id) yang tetap konstan sepanjang siklus hidupnya.1 Mereka merangkum perilaku (metode) yang beroperasi pada keadaan internalnya dan menegakkan invarian.12

C#


// Dalam YourApp.Domain.Common atau YourApp.Domain.Entities
public abstract class Entity<TId>
{
    public TId Id { get; protected set; }

    // Daftar peristiwa domain yang akan diterbitkan
    private readonly List<IDomainEvent> _domainEvents = new();
    public IReadOnlyCollection<IDomainEvent> DomainEvents => _domainEvents.AsReadOnly();

    protected void AddDomainEvent(IDomainEvent eventItem) => _domainEvents.Add(eventItem);
    public void ClearDomainEvents() => _domainEvents.Clear();

    // Meng-override Equals dan GetHashCode untuk perbandingan identitas
    public override bool Equals(object obj)
    {
        if (obj is not Entity<TId> otherEntity) return false;
        if (ReferenceEquals(this, otherEntity)) return true;
        if (GetType()!= otherEntity.GetType()) return false;
        return Id.Equals(otherEntity.Id);
    }

    public override int GetHashCode() => Id.GetHashCode();

    // Operator kesetaraan untuk kenyamanan
    public static bool operator ==(Entity<TId> left, Entity<TId> right)
    {
        if (ReferenceEquals(left, null)) return ReferenceEquals(right, null);
        return left.Equals(right);
    }

    public static bool operator!=(Entity<TId> left, Entity<TId> right)
    {
        return!(left == right);
    }
}

// Dalam YourApp.Domain.Entities
public class Product : Entity<Guid>
{
    public string Name { get; private set; }
    public Money Price { get; private set; } // Objek Nilai

    // Konstruktor privat untuk ORM, tetapi internal/privat untuk mengontrol pembuatan
    private Product() { }

    public Product(Guid id, string name, Money price)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Nama produk tidak boleh kosong.", nameof(name));
        if (price == null)
            throw new ArgumentNullException(nameof(price), "Harga produk tidak boleh null.");
        if (price.Amount < 0)
            throw new ArgumentException("Harga produk tidak boleh negatif.", nameof(price));

        Id = id;
        Name = name;
        Price = price;
    }

    public void UpdatePrice(Money newPrice)
    {
        // Aturan bisnis: Harga tidak boleh negatif
        if (newPrice.Amount < 0)
            throw new ArgumentException("Harga tidak boleh negatif.");

        // Aturan bisnis: Harga baru harus berbeda dari harga saat ini
        if (Price.Equals(newPrice)) return;

        Price = newPrice;
        AddDomainEvent(new ProductPriceUpdatedEvent(Id, newPrice));
    }

    public void Rename(string newName)
    {
        if (string.IsNullOrWhiteSpace(newName))
            throw new ArgumentException("Nama produk tidak boleh kosong.", nameof(newName));
        if (Name.Equals(newName, StringComparison.OrdinalIgnoreCase)) return; // Tidak ada perubahan

        Name = newName;
        AddDomainEvent(new ProductRenamedEvent(Id, newName));
    }
}



Merancang Objek Nilai yang Tidak Dapat Diubah (Immutable)

Objek Nilai diidentifikasi oleh nilainya, bukan identitasnya.10 Semua propertinya harus
readonly atau memiliki setter privat.11 Setiap "modifikasi" pada Objek Nilai sebenarnya mengembalikan instance baru.11 Penting untuk meng-override
Equals() dan GetHashCode() untuk kesetaraan berbasis nilai.11

C#


// Dalam YourApp.Domain.Common atau YourApp.Domain.ValueObjects
public abstract class ValueObject
{
    protected abstract IEnumerable<object> GetEqualityComponents();

    public override bool Equals(object obj)
    {
        if (obj == null |

| obj.GetType()!= GetType()) return false;
        var other = (ValueObject)obj;
        return GetEqualityComponents().SequenceEqual(other.GetEqualityComponents());
    }

    public override int GetHashCode()
    {
        return GetEqualityComponents()
           .Select(x => x!= null? x.GetHashCode() : 0)
           .Aggregate((x, y) => x ^ y);
    }

    // Operator kesetaraan untuk kenyamanan
    public static bool operator ==(ValueObject left, ValueObject right)
    {
        if (ReferenceEquals(left, null)) return ReferenceEquals(right, null);
        return left.Equals(right);
    }

    public static bool operator!=(ValueObject left, ValueObject right)
    {
        return!(left == right);
    }
}

// Dalam YourApp.Domain.ValueObjects
public class Money : ValueObject
{
    public decimal Amount { get; }
    public string Currency { get; }

    public Money(decimal amount, string currency)
    {
        if (string.IsNullOrWhiteSpace(currency))
            throw new ArgumentException("Mata uang tidak boleh null atau kosong.");
        if (amount < 0)
            throw new ArgumentException("Jumlah uang tidak boleh negatif.");
        // Tambahkan validasi mata uang lebih lanjut jika diperlukan (misalnya, kode ISO 4217)

        Amount = amount;
        Currency = currency.ToUpperInvariant(); // Standardisasi mata uang
    }

    protected override IEnumerable<object> GetEqualityComponents()
    {
        yield return Amount;
        yield return Currency;
    }

    // Contoh metode spesifik domain yang mengembalikan instance baru
    public Money Add(Money other)
    {
        if (Currency!= other.Currency)
            throw new InvalidOperationException("Tidak dapat menambahkan uang dengan mata uang yang berbeda.");
        return new Money(Amount + other.Amount, Currency);
    }

    public Money Subtract(Money other)
    {
        if (Currency!= other.Currency)
            throw new InvalidOperationException("Tidak dapat mengurangi uang dengan mata uang yang berbeda.");
        return new Money(Amount - other.Amount, Currency);
    }
}


Distingsi antara Entitas yang dapat berubah dan Objek Nilai yang tidak dapat diubah bukan hanya konsep teoretis, melainkan filosofi desain yang sangat memengaruhi cara perubahan keadaan dikelola dan dipahami dalam domain. Dengan membuat Objek Nilai tidak dapat diubah, DDD memastikan bahwa "nilai" mereka tetap konsisten di seluruh sistem, menyederhanakan penalaran tentang keadaannya dan mencegah efek samping yang tidak diinginkan. Sebaliknya, Entitas, dengan keadaan yang dapat berubah, menjadi titik fokus untuk perilaku yang mengubah model domain. Aggregate Root kemudian bertindak sebagai penjaga perubahan ini, memastikan bahwa semua mutasi (baik pada keadaannya sendiri maupun entitas/VO yang dikandungnya) mematuhi invarian agregat. Pilihan yang disengaja antara mutabilitas dan immutabilitas pada berbagai tingkatan ini secara drastis meningkatkan kejelasan model domain dan mengurangi kemungkinan bug yang terkait dengan keadaan yang tidak konsisten. Pilihan desain ini secara langsung mendukung kemampuan pengujian (VO yang tidak dapat diubah mudah diuji) dan pemeliharaan, karena aliran perubahan keadaan eksplisit dan terkontrol. Ini juga memiliki implikasi untuk persistensi, karena ORM perlu menangani entitas yang dapat berubah dan objek nilai yang tidak dapat diubah dengan benar (misalnya, entitas yang dimiliki EF Core atau konverter nilai).

Membuat Agregat dan Aggregate Root untuk Konsistensi

Aggregate Root adalah satu-satunya titik masuk untuk operasi dalam agregat.13 Koleksi internal bersifat privat/internal, diekspos sebagai
IReadOnlyCollection<T>.12 Metode pada AR merangkum logika bisnis dan menegakkan invarian.13

C#


// Dalam YourApp.Domain.Aggregates.OrderAggregate
public enum OrderStatus { PaymentPending, ReadyForShipping, InTransit, Delivered, Cancelled }

public class Order : Entity<Guid>
{
    private readonly List<OrderItem> _items = new();
    public DateTime CreationDate { get; private set; }
    public decimal PaidAmount { get; private set; }
    public OrderStatus Status { get; private set; }

    public IReadOnlyCollection<OrderItem> Items => _items.AsReadOnly();
    public decimal TotalAmount => _items.Sum(item => item.Quantity * item.UnitPrice.Amount);

    // Konstruktor privat untuk ORM
    private Order() { }

    public Order(Guid id, DateTime creationDate)
    {
        Id = id;
        CreationDate = creationDate;
        Status = OrderStatus.PaymentPending; // Invarian awal
        AddDomainEvent(new OrderCreatedEvent(Id));
    }

    public void AddItem(Product product, int quantity)
    {
        if (Status!= OrderStatus.PaymentPending)
            throw new InvalidOperationException("Tidak dapat menambahkan item ke pesanan yang sudah dikonfirmasi.");
        if (quantity <= 0)
            throw new ArgumentException("Kuantitas harus positif.", nameof(quantity));

        var existingItem = _items.FirstOrDefault(i => i.ProductId == product.Id);
        if (existingItem!= null)
        {
            existingItem.UpdateQuantity(existingItem.Quantity + quantity);
        }
        else
        {
            _items.Add(new OrderItem(Guid.NewGuid(), Id, product.Id, product.Name, product.Price, quantity));
        }
        AddDomainEvent(new OrderItemAddedEvent(Id, product.Id, quantity));
    }

    public void RemoveItem(Guid orderItemId)
    {
        if (Status!= OrderStatus.PaymentPending)
            throw new InvalidOperationException("Tidak dapat menghapus item dari pesanan yang sudah dikonfirmasi.");

        var itemToRemove = _items.FirstOrDefault(i => i.Id == orderItemId);
        if (itemToRemove == null)
            throw new InvalidOperationException($"Item pesanan dengan ID {orderItemId} tidak ditemukan.");

        _items.Remove(itemToRemove);
        AddDomainEvent(new OrderItemRemovedEvent(Id, orderItemId));
    }

    public void ConfirmPayment(decimal amount)
    {
        if (amount <= 0) throw new ArgumentException("Jumlah pembayaran harus positif.");
        if (Status!= OrderStatus.PaymentPending) throw new InvalidOperationException("Pesanan tidak dalam status menunggu pembayaran.");
        if (!_items.Any()) throw new InvalidOperationException("Pesanan harus memiliki item untuk dibayar.");

        PaidAmount += amount;

        if (PaidAmount >= TotalAmount)
        {
            Status = OrderStatus.ReadyForShipping;
            AddDomainEvent(new OrderPaidEvent(Id, PaidAmount));
        }
    }

    public void ShipOrder()
    {
        if (Status!= OrderStatus.ReadyForShipping)
            throw new InvalidOperationException("Pesanan harus siap untuk dikirim sebelum dapat dikirim.");
        if (!_items.Any())
            throw new InvalidOperationException("Tidak dapat mengirim pesanan tanpa item.");

        Status = OrderStatus.InTransit;
        AddDomainEvent(new OrderShippedEvent(Id));
    }
}

// Dalam YourApp.Domain.Aggregates.OrderAggregate
public class OrderItem : Entity<Guid>
{
    public Guid OrderId { get; private set; }
    public Guid ProductId { get; private set; }
    public string ItemName { get; private set; }
    public Money UnitPrice { get; private set; } // Objek Nilai
    public int Quantity { get; private set; }

    // Konstruktor privat untuk ORM
    private OrderItem() { }

    internal OrderItem(Guid id, Guid orderId, Guid productId, string itemName, Money unitPrice, int quantity)
    {
        if (string.IsNullOrWhiteSpace(itemName))
            throw new ArgumentException("Nama item tidak boleh kosong.", nameof(itemName));
        if (unitPrice == null)
            throw new ArgumentNullException(nameof(unitPrice), "Harga satuan tidak boleh null.");
        if (quantity <= 0)
            throw new ArgumentException("Kuantitas harus positif.", nameof(quantity));

        Id = id;
        OrderId = orderId;
        ProductId = productId;
        ItemName = itemName;
        UnitPrice = unitPrice;
        Quantity = quantity;
    }

    internal void UpdateQuantity(int newQuantity)
    {
        if (newQuantity <= 0)
            throw new ArgumentException("Kuantitas harus positif.", nameof(newQuantity));
        Quantity = newQuantity;
    }
}



Mendefinisikan Layanan Domain untuk Logika Lintas Agregat

Layanan Domain digunakan untuk logika bisnis yang melibatkan beberapa agregat atau ketergantungan eksternal.16 Mereka harus tanpa status (stateless).16

C#


// Dalam YourApp.Domain.Services
public interface IDomainService { } // Antarmuka penanda opsional

public class OrderPlacementService : IDomainService
{
    private readonly IProductRepository _productRepository; // Repositori untuk agregat Produk
    private readonly IOrderRepository _orderRepository;     // Repositori untuk agregat Pesanan

    public OrderPlacementService(IProductRepository productRepository, IOrderRepository orderRepository)
    {
        _productRepository = productRepository;
        _orderRepository = orderRepository;
    }

    public async Task<Order> PlaceOrderAsync(Guid customerId, Dictionary<Guid, int> productQuantities)
    {
        // Logika yang melibatkan beberapa agregat (Produk, Pesanan)
        var order = new Order(Guid.NewGuid(), DateTime.UtcNow);

        foreach (var entry in productQuantities)
        {
            var product = await _productRepository.GetByIdAsync(entry.Key);
            if (product == null)
                throw new ProductNotFoundException($"Produk dengan ID {entry.Key} tidak ditemukan.");

            // Asumsi stok produk cukup, atau ini ditangani oleh agregat Inventaris terpisah
            order.AddItem(product, entry.Value);
        }

        await _orderRepository.AddAsync(order);
        // Berpotensi memicu peristiwa integrasi di sini jika bounded context lain perlu tahu
        return order;
    }
}

// Contoh pengecualian domain
public class ProductNotFoundException : Exception
{
    public ProductNotFoundException(Guid productId)
        : base($"Produk dengan ID {productId} tidak ditemukan.") { }
}



Memicu dan Menangani Peristiwa Domain

Peristiwa Domain mewakili sesuatu yang signifikan yang terjadi dalam domain.6 Mereka dipicu oleh agregat atau layanan domain 17 dan ditangani oleh event handler yang melakukan efek samping atau memicu logika domain lainnya.17 Peristiwa Domain adalah sistem perpesanan internal dari suatu bounded context, memungkinkan komponen dalam konteks tersebut untuk bereaksi terhadap kejadian domain yang signifikan tanpa coupling langsung. Pendekatan "reaktif" ini berarti bahwa alih-alih meng-coupling komponen secara erat (misalnya,
OrderService secara langsung memanggil EmailService), agregat Order cukup memublikasikan OrderCompletedEvent. Sejumlah handler kemudian dapat berlangganan peristiwa ini, memungkinkan fungsionalitas baru (seperti mengirim email, memperbarui poin loyalitas, atau logging) ditambahkan tanpa memodifikasi logika domain inti. Ini adalah mekanisme yang kuat untuk mencapai kohesi tinggi dan coupling rendah di dalam satu bounded context.

C#


// Dalam YourApp.Domain.Events
public interface IDomainEvent { }

public record OrderCreatedEvent(Guid OrderId) : IDomainEvent;
public record ProductPriceUpdatedEvent(Guid ProductId, Money NewPrice) : IDomainEvent;
public record OrderItemAddedEvent(Guid OrderId, Guid ProductId, int Quantity) : IDomainEvent;
public record OrderPaidEvent(Guid OrderId, decimal AmountPaid) : IDomainEvent;
public record OrderShippedEvent(Guid OrderId) : IDomainEvent;
public record ProductRenamedEvent(Guid ProductId, string NewName) : IDomainEvent;

// Antarmuka untuk handler peristiwa domain (dapat menggunakan MediatR untuk implementasi yang lebih canggih)
public interface IDomainEventHandler<TEvent> where TEvent : IDomainEvent
{
    Task Handle(TEvent domainEvent, CancellationToken cancellationToken);
}

// Implementasi sederhana dispatcher peristiwa domain (untuk ilustrasi, MediatR lebih baik untuk aplikasi nyata)
public static class DomainEvents
{
    // Menggunakan ThreadStatic untuk memastikan daftar peristiwa terisolasi per thread/permintaan HTTP
   
    private static List<IDomainEvent> _domainEvents;

    public static void Add(IDomainEvent eventItem)
    {
        _domainEvents??= new List<IDomainEvent>();
        _domainEvents.Add(eventItem);
    }

    public static IReadOnlyCollection<IDomainEvent> GetEvents() => _domainEvents?.AsReadOnly()?? new List<IDomainEvent>().AsReadOnly();

    public static void ClearEvents() => _domainEvents = null;

    // Metode untuk menerbitkan peristiwa (biasanya dipanggil setelah SaveChanges di Unit of Work)
    public static async Task Publish(IServiceProvider serviceProvider, IReadOnlyCollection<IDomainEvent> events)
    {
        foreach (var domainEvent in events)
        {
            // Menggunakan ServiceProvider untuk mendapatkan handler yang sesuai
            // Dalam aplikasi nyata, ini akan lebih canggih (misalnya, menggunakan MediatR.Publish)
            var handlerType = typeof(IDomainEventHandler<>).MakeGenericType(domainEvent.GetType());
            var handlers = serviceProvider.GetServices(handlerType);

            foreach (dynamic handler in handlers)
            {
                await handler.Handle((dynamic)domainEvent, CancellationToken.None);
            }
        }
    }
}

// Contoh handler peristiwa domain (dapat berada di Lapisan Aplikasi atau Infrastruktur)
// Dalam aplikasi nyata, ini akan didaftarkan melalui DI dan dipicu oleh MediatR
public class OrderCreatedLogger : IDomainEventHandler<OrderCreatedEvent>
{
    private readonly ILogger<OrderCreatedLogger> _logger;

    public OrderCreatedLogger(ILogger<OrderCreatedLogger> logger) => _logger = logger;

    public Task Handle(OrderCreatedEvent domainEvent, CancellationToken cancellationToken)
    {
        _logger.LogInformation($" Pesanan baru dibuat: {domainEvent.OrderId}");
        return Task.CompletedTask;
    }
}

public class ProductPriceChangeNotifier : IDomainEventHandler<ProductPriceUpdatedEvent>
{
    private readonly ILogger<ProductPriceChangeNotifier> _logger;

    public ProductPriceChangeNotifier(ILogger<ProductPriceChangeNotifier> logger) => _logger = logger;

    public Task Handle(ProductPriceUpdatedEvent domainEvent, CancellationToken cancellationToken)
    {
        _logger.LogInformation($" Harga produk {domainEvent.ProductId} diperbarui menjadi {domainEvent.NewPrice.Amount} {domainEvent.NewPrice.Currency}.");
        // Logika untuk mengirim notifikasi ke sistem lain atau pengguna
        return Task.CompletedTask;
    }
}



3. Mengintegrasikan DDD dengan Entity Framework Core dan Pola Repositori

Integrasi Domain-Driven Design dengan persistensi data, khususnya menggunakan Entity Framework Core (EF Core) dan Pola Repositori, adalah aspek krusial dalam membangun aplikasi ASP.NET Core yang kuat.

Integrasi Konseptual: DDD dengan Penggunaan Langsung EF Core

Entity Framework Core adalah Object-Relational Mapper (ORM) yang banyak digunakan di ekosistem.NET untuk persistensi data.3
DbContext EF Core secara inheren menggabungkan pola Unit of Work dan Repositori, memungkinkan penggunaannya secara langsung dari pengontrol atau layanan aplikasi untuk operasi CRUD yang lebih sederhana.12 Untuk skenario yang tidak terlalu kompleks, penggunaan langsung
DbContext dapat menghasilkan kode yang paling sederhana dan paling cepat untuk diimplementasikan.12
Namun, prinsip-prinsip DDD menganjurkan enkapsulasi perilaku dan aturan domain di dalam entitas dan agregat, mengontrol akses ke koleksi internal.12 EF Core versi 1.1 dan yang lebih baru mendukung penggunaan
field privat dan koleksi read-only (IReadOnlyCollection<T>) untuk menyelaraskan dengan persyaratan enkapsulasi DDD, mencegah modifikasi arbitrer dari luar terhadap keadaan internal agregat.12 Ini memungkinkan model domain yang kaya tetap utuh bahkan saat menggunakan fitur ORM.

Pelapisan DDD dengan Pola Repositori dan EF Core

Meskipun penggunaan langsung DbContext dimungkinkan, mengimplementasikan pola Repositori kustom di atas EF Core memberikan beberapa manfaat signifikan dalam konteks DDD, terutama untuk microservices atau aplikasi yang lebih kompleks.12

Mengapa Menggunakan Pola Repositori Kustom dengan EF Core?

Abstraksi dan Pemisahan Kekhawatiran: Repositori menyediakan antarmuka antara lapisan akses data dan logika bisnis, merangkum detail persistensi.12 Ini berarti logika domain tidak perlu mengetahui bagaimana data disimpan atau diambil.
Decoupling: Pola Repositori mendekopel lapisan aplikasi dan domain dari lapisan persistensi infrastruktur.12 Ini membuat transisi ke ORM atau database yang berbeda jauh lebih mudah dengan perubahan kode yang minimal.24 Hal ini sangat selaras dengan filosofi DDD untuk menjaga logika domain tetap independen dari detail database.6 Pola Repositori, ketika diimplementasikan dengan benar (dengan antarmuka di domain dan implementasi konkret di infrastruktur), bukan hanya tentang mengatur kode akses data; ini adalah mekanisme decoupling strategis yang memberikan fleksibilitas arsitektur yang signifikan. Ini menciptakan kemampuan "plug-and-play" untuk persistensi. Ini berarti bahwa jika suatu organisasi memutuskan untuk beralih dari SQL Server ke database NoSQL, atau bahkan ORM yang berbeda, logika bisnis inti di lapisan Domain dan Aplikasi sebagian besar tetap tidak tersentuh. Future-proofing ini sangat berharga untuk aplikasi perusahaan yang berumur panjang, mengurangi biaya dan risiko perubahan teknologi besar.
Kemampuan Pengujian: Repositori dapat dengan mudah di-mock untuk pengujian unit, memungkinkan logika bisnis diuji secara terpisah tanpa bergantung pada database sungguhan.24
Menghindari Ketergantungan Langsung: Menggunakan repositori mencegah lapisan aplikasi secara langsung bergantung pada DbContext, yang akan melanggar Prinsip Inversi Dependensi.24

Mendefinisikan Antarmuka Repositori di Lapisan Domain

Antarmuka repositori harus didefinisikan di Lapisan Domain (atau Lapisan Aplikasi, tergantung pada preferensi, tetapi Domain adalah yang paling bersih untuk abstraksi murni).13 Antarmuka ini mengabstraksi operasi akses data untuk agregat.6 Idealnya, harus ada hubungan satu-ke-satu antara aggregate root dan repositori terkaitnya.12 Metode-metode repositori harus beroperasi pada aggregate root, bukan pada entitas individual di dalam agregat, untuk menjaga konsistensi agregat.13

C#


// Dalam YourApp.Domain.Interfaces.Repositories
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(Guid id);
    Task AddAsync(Order order);
    Task UpdateAsync(Order order);
    Task DeleteAsync(Order order);
    // Tambahkan metode untuk kebutuhan kueri spesifik yang mengembalikan agregat, bukan IQueryable
    // Contoh: Task<IReadOnlyList<Order>> GetOrdersByCustomerIdAsync(Guid customerId);
}

public interface IProductRepository
{
    Task<Product?> GetByIdAsync(Guid id);
    Task AddAsync(Product product);
    Task UpdateAsync(Product product);
    Task DeleteAsync(Product product);
}



Mengimplementasikan Repositori di Lapisan Infrastruktur

Implementasi konkret dari antarmuka repositori berada di Lapisan Infrastruktur.3 Lapisan ini menangani
DbContext EF Core, pemetaan, dan interaksi database aktual.3 Seringkali, model data terpisah (POCO) digunakan untuk pemetaan database untuk menghindari pencemaran entitas domain dengan kekhawatiran persistensi.13 Pustaka seperti AutoMapper dapat digunakan untuk memetakan antara entitas domain dan model data.13

C#


// Dalam YourApp.Infrastructure.Data.Models (Model data untuk EF Core)
// Ini adalah objek POCO yang dioptimalkan untuk persistensi database
public class OrderModel
{
    public Guid Id { get; set; }
    public DateTime CreationDate { get; set; }
    public decimal PaidAmount { get; set; }
    public OrderStatus Status { get; set; } // Enum dapat dipetakan langsung
    public ICollection<OrderItemModel> Items { get; set; } = new List<OrderItemModel>();
}

public class OrderItemModel
{
    public Guid Id { get; set; }
    public Guid OrderId { get; set; }
    public Guid ProductId { get; set; }
    public string ItemName { get; set; }
    public decimal UnitPriceAmount { get; set; } // Bagian dari Value Object Money
    public string UnitPriceCurrency { get; set; } // Bagian dari Value Object Money
    public int Quantity { get; set; }
}

public class ProductModel
{
    public Guid Id { get; set; }
    public string Name { get; set; }
    public decimal PriceAmount { get; set; }
    public string PriceCurrency { get; set; }
}

// Dalam YourApp.Infrastructure.Data.Repositories
public class OrderRepository : IOrderRepository
{
    private readonly ApplicationDbContext _dbContext;
    private readonly IMapper _mapper; // Menggunakan AutoMapper untuk pemetaan

    public OrderRepository(ApplicationDbContext dbContext, IMapper mapper)
    {
        _dbContext = dbContext;
        _mapper = mapper;
    }

    public async Task<Order?> GetByIdAsync(Guid id)
    {
        // Eager loading untuk konsistensi agregat
        var orderModel = await _dbContext.Orders
           .Include(o => o.Items)
           .FirstOrDefaultAsync(o => o.Id == id);

        if (orderModel == null) return null;

        // Memetakan model data ke entitas domain
        return _mapper.Map<Order>(orderModel);
    }

    public async Task AddAsync(Order order)
    {
        var orderModel = _mapper.Map<OrderModel>(order); // Memetakan entitas domain ke model data
        _dbContext.Orders.Add(orderModel);
        await _dbContext.SaveChangesAsync();
        // Perbarui ID entitas domain jika dihasilkan oleh DB (misalnya, jika ID adalah int auto-increment)
        _mapper.Map(orderModel, order); // Memastikan entitas domain memiliki ID yang dihasilkan DB
    }

    public async Task UpdateAsync(Order order)
    {
        var orderModel = _mapper.Map<OrderModel>(order);
        var existingOrderModel = await _dbContext.Orders
           .Include(o => o.Items)
           .SingleAsync(o => o.Id == order.Id);

        // Memperbarui nilai properti root agregat
        _dbContext.Entry(existingOrderModel).CurrentValues.SetValues(orderModel);

        // Logika kompleks untuk memperbarui koleksi anak (OrderItem)
        // Ini adalah bagian yang paling rumit dalam mengelola agregat dengan EF Core
        // Strategi: hapus item yang tidak ada di domain, perbarui yang ada, tambahkan yang baru
        var currentItemModels = existingOrderModel.Items.ToList();
        foreach (var itemModel in currentItemModels)
        {
            if (!orderModel.Items.Any(oi => oi.Id == itemModel.Id))
            {
                _dbContext.Remove(itemModel); // Hapus item yang tidak lagi ada
            }
        }

        foreach (var newItemModel in orderModel.Items)
        {
            var existingItem = currentItemModels.FirstOrDefault(i => i.Id == newItemModel.Id);
            if (existingItem!= null)
            {
                _dbContext.Entry(existingItem).CurrentValues.SetValues(newItemModel); // Perbarui item yang ada
            }
            else
            {
                existingOrderModel.Items.Add(newItemModel); // Tambahkan item baru
            }
        }

        await _dbContext.SaveChangesAsync();
    }

    public async Task DeleteAsync(Order order)
    {
        var orderModel = await _dbContext.Orders.FindAsync(order.Id);
        if (orderModel!= null)
        {
            _dbContext.Orders.Remove(orderModel);
            await _dbContext.SaveChangesAsync();
        }
    }
}

// Dalam YourApp.Infrastructure.Data.Mappings (Profil AutoMapper)
public class DomainToDataModelMappingProfile : Profile
{
    public DomainToDataModelMappingProfile()
    {
        CreateMap<Order, OrderModel>()
           .ForMember(dest => dest.Status, opt => opt.MapFrom(src => src.Status))
           .ForMember(dest => dest.Items, opt => opt.MapFrom(src => src.Items)); // Mapping koleksi anak

        CreateMap<OrderModel, Order>()
           .ForCtorParam("id", opt => opt.MapFrom(src => src.Id))
           .ForCtorParam("creationDate", opt => opt.MapFrom(src => src.CreationDate))
           .ForMember(dest => dest.PaidAmount, opt => opt.MapFrom(src => src.PaidAmount))
           .ForMember(dest => dest.Status, opt => opt.MapFrom(src => src.Status))
           .ForMember(dest => dest.Items, opt => opt.Ignore()) // Items akan diisi secara manual atau melalui konstruktor internal
           .AfterMap((src, dest) =>
            {
                // Rehidrasi OrderItems ke dalam agregat
                foreach (var itemModel in src.Items)
                {
                    var orderItem = new OrderItem(itemModel.Id, itemModel.OrderId, itemModel.ProductId, itemModel.ItemName, new Money(itemModel.UnitPriceAmount, itemModel.UnitPriceCurrency), itemModel.Quantity);
                    // Menggunakan refleksi atau metode internal jika OrderItem tidak memiliki setter publik
                    // dest._items.Add(orderItem); // Ini membutuhkan akses ke field privat _items
                    // Cara yang lebih baik adalah melalui konstruktor atau metode internal Order
                    // Untuk contoh ini, kita asumsikan ada cara internal untuk menambahkan item yang sudah ada
                    // Jika tidak, agregat harus dibangun ulang dari data model
                }
            });

        CreateMap<OrderItem, OrderItemModel>()
           .ForMember(dest => dest.UnitPriceAmount, opt => opt.MapFrom(src => src.UnitPrice.Amount))
           .ForMember(dest => dest.UnitPriceCurrency, opt => opt.MapFrom(src => src.UnitPrice.Currency));

        CreateMap<OrderItemModel, OrderItem>()
           .ForCtorParam("id", opt => opt.MapFrom(src => src.Id))
           .ForCtorParam("orderId", opt => opt.MapFrom(src => src.OrderId))
           .ForCtorParam("productId", opt => opt.MapFrom(src => src.ProductId))
           .ForCtorParam("itemName", opt => opt.MapFrom(src => src.ItemName))
           .ForCtorParam("unitPrice", opt => opt.MapFrom(src => new Money(src.UnitPriceAmount, src.UnitPriceCurrency)))
           .ForCtorParam("quantity", opt => opt.MapFrom(src => src.Quantity));

        CreateMap<Product, ProductModel>()
           .ForMember(dest => dest.PriceAmount, opt => opt.MapFrom(src => src.Price.Amount))
           .ForMember(dest => dest.PriceCurrency, opt => opt.MapFrom(src => src.Price.Currency));

        CreateMap<ProductModel, Product>()
           .ForCtorParam("id", opt => opt.MapFrom(src => src.Id))
           .ForCtorParam("name", opt => opt.MapFrom(src => src.Name))
           .ForCtorParam("price", opt => opt.MapFrom(src => new Money(src.PriceAmount, src.PriceCurrency)));
    }
}



Praktik Terbaik untuk Desain Repositori

Satu-ke-satu dengan Aggregate Root: Setiap repositori harus mengelola satu aggregate root.12 Ini memastikan konsistensi transaksional dalam agregat dan menyederhanakan tanggung jawab repositori.
Enkapsulasi: Repositori harus mengembalikan aggregate root yang sepenuhnya konsisten, bukan IQueryable<T> yang mengekspos detail internal atau memungkinkan kueri eksternal untuk melewati invarian agregat.12 Pilihan bagaimana repositori berinteraksi dengan model domain secara langsung memengaruhi apakah aplikasi menyerah pada anti-pola "Anemic Domain Model". Jika repositori mengembalikan struktur data sederhana (DTO atau POCO) yang tidak memiliki perilaku, atau jika mereka mengekspos
IQueryable<T> yang memungkinkan manipulasi eksternal, logika bisnis cenderung bocor ke layanan aplikasi atau bahkan pengontrol. Ini merusak prinsip inti DDD dari model domain yang kaya di mana perilaku dan data dienkapsulasi. Repositori praktik terbaik harus mengembalikan dan mempertahankan aggregate root, memastikan bahwa semua interaksi dengan model domain melalui perilaku terkontrol agregat, sehingga mencegah model anemic dan mempertahankan invarian.12
Metode Persistensi: Fokus pada metode yang memperbarui keadaan entitas di dalam agregat terkait.12 Kueri harus mengembalikan agregat, bukan model data mentah.13
Unit of Work: DbContext bertindak sebagai Unit of Work, dibagikan antara beberapa repositori dalam cakupan permintaan HTTP yang sama.12 Ini memastikan bahwa semua perubahan dalam satu operasi bisnis disimpan sebagai satu transaksi atomik.

4. Kombinasi Arsitektur Lanjutan dengan DDD

DDD sangat kuat ketika dikombinasikan dengan pola arsitektur lain seperti Clean Architecture, CQRS, dan Event-Driven Architecture. Kombinasi ini memungkinkan pembangunan sistem yang sangat skalabel, maintainable, dan responsif.

DDD + Clean Architecture

Clean Architecture, juga dikenal sebagai Onion Architecture, Hexagonal Architecture, atau Ports-and-Adapters, adalah pola arsitektur yang mengatur kode menjadi lapisan konsentris dengan dependensi yang selalu mengarah ke dalam.19 Arsitektur ini menyediakan kerangka struktural yang secara fisik menegakkan pemisahan logis yang dianjurkan oleh DDD. Sementara DDD mendefinisikan
apa yang harus dipisahkan (konsep domain, logika bisnis), Clean Architecture mendikte bagaimana pemisahan ini dicapai melalui aturan dependensi yang ketat (aliran ke dalam). Pola arsitektur ini bertindak sebagai penjaga, mencegah jebakan umum seperti logika domain yang bocor ke kekhawatiran infrastruktur atau detail UI. Ini memastikan bahwa domain inti tetap menjadi inti aplikasi yang murni, dapat diuji, dan stabil, benar-benar independen dari kerangka kerja eksternal atau database.21

Struktur Proyek dan Aliran Dependensi

Lapisan Domain (Core): Ini adalah inti dari aplikasi. Berisi entitas, objek nilai, agregat, peristiwa domain, layanan domain, dan antarmuka (misalnya, untuk repositori).3 Lapisan ini tidak memiliki ketergantungan pada lapisan luar.20
Lapisan Aplikasi: Berisi logika bisnis spesifik aplikasi, kasus penggunaan, DTO, perintah (commands), kueri (queries), dan handler-nya.3 Lapisan ini bergantung pada Lapisan Domain.20
Lapisan Infrastruktur: Mengimplementasikan antarmuka yang didefinisikan di Lapisan Domain dan Aplikasi. Menangani detail teknis seperti database (Entity Framework Core), layanan eksternal, dan implementasi repositori konkret.3 Lapisan ini bergantung pada Lapisan Domain dan Aplikasi.22
Lapisan Presentasi (ASP.NET Core Web API/MVC): Lapisan terluar yang menangani permintaan UI/API, pemetaan DTO, pengontrol, dan konfigurasi injeksi dependensi.3 Lapisan ini bergantung pada Lapisan Aplikasi.22
Aturan dependensi yang ketat memastikan bahwa lapisan dalam (inti bisnis) tidak memiliki ketergantungan pada lapisan luar (detail implementasi), sehingga inti tetap stabil dan dapat diuji.20

Mengintegrasikan Pola Repositori dalam Clean Architecture

Antarmuka repositori (misalnya, IOrderRepository) didefinisikan di Lapisan Domain.13 Implementasi konkretnya (misalnya,
OrderRepository menggunakan EF Core) berada di Lapisan Infrastruktur.3 Layanan lapisan aplikasi atau handler perintah bergantung pada
antarmuka repositori (IOrderRepository), bukan implementasi konkretnya, yang menjunjung tinggi Prinsip Inversi Dependensi.23



Struktur Proyek Konseptual:

Solution
├── YourApp.Domain (Core)
│   ├── Entities
│   ├── ValueObjects
│   ├── Aggregates
│   ├── DomainEvents
│   ├── DomainServices
│   └── Interfaces (e.g., IOrderRepository, IProductRepository)
├── YourApp.Application
│   ├── Commands (Input DTOs untuk write operations)
│   ├── Queries (Input DTOs untuk read operations)
│   ├── Handlers (Implementasi IRequestHandler untuk Commands dan Queries)
│   ├── DTOs (Output DTOs untuk presentasi)
│   └── Services (Layanan aplikasi yang mengorkestrasi kasus penggunaan)
├── YourApp.Infrastructure
│   ├── Data (DbContext, Migrations, Konfigurasi Entitas EF Core)
│   ├── Repositories (Implementasi konkret dari IOrderRepository, IProductRepository)
│   ├── ExternalServices (e.g., EmailSender, PaymentGatewayClient)
│   └── DependencyInjection (Registrasi DI khusus infrastruktur)
└── YourApp.Api (Presentation)
    ├── Controllers
    ├── appsettings.json
    ├── Program.cs (Setup DI, middleware, konfigurasi pipeline)
    └── Mappings (Profil AutoMapper untuk pemetaan DTO)



Tabel: Tanggung Jawab Lapisan Clean Architecture

Lapisan
Tanggung Jawab Utama
Isi Kunci (Contoh)
Ketergantungan
Domain
Logika bisnis inti perusahaan, aturan, dan model data yang fundamental.
Entitas, Objek Nilai, Agregat, Peristiwa Domain, Layanan Domain, Antarmuka Repositori.
Tidak ada (hanya tipe primitif.NET CLR).
Aplikasi
Logika bisnis spesifik aplikasi, kasus penggunaan, orkestrasi aliran data.
Perintah (Commands), Kueri (Queries), Handler Perintah/Kueri, DTO (Input/Output), Layanan Aplikasi.
Lapisan Domain.
Infrastruktur
Implementasi teknis detail, akses data, dan layanan eksternal.
Implementasi Repositori (EF Core), DbContext, Migrasi, Klien Layanan Eksternal (Email, SMS).
Lapisan Domain, Lapisan Aplikasi.
Presentasi
Antarmuka pengguna (UI) atau API, menangani permintaan, dan menyajikan data.
Pengontrol (Controllers), Model Tampilan (View Models untuk MVC), DTO (untuk API), Konfigurasi Injeksi Dependensi.
Lapisan Aplikasi.


CQRS dengan MediatR dalam Konteks DDD

Command Query Responsibility Segregation (CQRS) adalah pola arsitektur yang memisahkan operasi menjadi dua kategori yang berbeda: Perintah (Commands) yang mengubah keadaan aplikasi tanpa mengembalikan data, dan Kueri (Queries) yang mengembalikan data tanpa mengubah keadaan.25 Pemisahan ini mengatasi tantangan arsitektur CRUD tradisional, seperti ketidakcocokan data, konflik penguncian, masalah kinerja, dan tantangan keamanan.28
Manfaat utama CQRS meliputi skalabilitas independen dari model baca dan tulis, skema data yang dioptimalkan untuk kueri dan pembaruan, peningkatan keamanan dengan membatasi izin tulis, pemisahan kekhawatiran yang lebih baik, dan kueri yang lebih sederhana.28 Pendorong utama untuk mengadopsi CQRS seringkali adalah optimalisasi skalabilitas dan kinerja, terutama dalam sistem dengan rasio baca-ke-tulis yang tinggi. Dengan memungkinkan model yang berbeda dan bahkan penyimpanan data yang terpisah untuk operasi baca dan tulis, CQRS memungkinkan penyetelan dan penskalaan independen dari operasi ini. Namun, optimalisasi ini datang dengan trade-off arsitektur yang signifikan:
konsistensi eventual.28 Ketika model baca dan tulis dipisahkan, ada penundaan inheren dalam sinkronisasi data, yang berarti pengguna mungkin melihat data yang usang. Konsistensi eventual ini bukan cacat melainkan pilihan desain yang disengaja untuk mencapai kinerja dan ketersediaan yang lebih tinggi. Ini membutuhkan pertimbangan cermat terhadap pengalaman pengguna (misalnya, "tampilan optimis" di UI, memberi tahu pengguna tentang pembaruan yang tertunda) dan mekanisme yang kuat untuk sinkronisasi (misalnya, handler peristiwa yang memperbarui model baca).30

Mengimplementasikan Perintah dan Kueri dengan MediatR

MediatR adalah pustaka ringan yang mengimplementasikan pola mediator, menyederhanakan perpesanan dalam proses dan memfasilitasi arsitektur yang digabungkan secara longgar.26 Perintah dan Kueri didefinisikan sebagai kelas yang mengimplementasikan antarmuka
IRequest<TResponse> MediatR.26 Setiap perintah/kueri memiliki handler khusus yang mengimplementasikan antarmuka
IRequestHandler<TRequest, TResponse>.26
Perintah (Commands): Mewakili tugas bisnis spesifik (misalnya, "Pesan kamar hotel" alih-alih "Set ReservationStatus menjadi Reserved").28 Handler perintah berisi logika untuk mengeksekusi perintah, seringkali melibatkan aggregate root dan repositori.26
Kueri (Queries): Tidak pernah mengubah data. Mengembalikan Data Transfer Objects (DTO) tanpa logika domain, dioptimalkan untuk presentasi.28 Handler kueri mengambil data, seringkali langsung dari model baca atau lapisan kueri yang dioptimalkan.26
Pengontrol menginjeksi IMediator untuk mengirim perintah/kueri ke handler yang sesuai.26

C#


// Dalam YourApp.Application.Commands
public class AddItemToOrderCommand : IRequest<Guid>
{
    public Guid OrderId { get; set; }
    public Guid ProductId { get; set; }
    public int Quantity { get; set; }
}

// Dalam YourApp.Application.Queries
public class GetOrderDetailsQuery : IRequest<OrderDetailsDto>
{
    public Guid OrderId { get; set; }
}

// Dalam YourApp.Application.Handlers
public class AddItemToOrderCommandHandler : IRequestHandler<AddItemToOrderCommand, Guid>
{
    private readonly IOrderRepository _orderRepository;
    private readonly IProductRepository _productRepository;

    public AddItemToOrderCommandHandler(IOrderRepository orderRepository, IProductRepository productRepository)
    {
        _orderRepository = orderRepository;
        _productRepository = productRepository;
    }

    public async Task<Guid> Handle(AddItemToOrderCommand request, CancellationToken cancellationToken)
    {
        var order = await _orderRepository.GetByIdAsync(request.OrderId);
        if (order == null) throw new OrderNotFoundException(request.OrderId);

        var product = await _productRepository.GetByIdAsync(request.ProductId);
        if (product == null) throw new ProductNotFoundException(request.ProductId);

        order.AddItem(product, request.Quantity); // Logika domain pada agregat
        await _orderRepository.UpdateAsync(order);
        return order.Id;
    }
}

// Dalam YourApp.Application.Handlers
public class GetOrderDetailsQueryHandler : IRequestHandler<GetOrderDetailsQuery, OrderDetailsDto>
{
    private readonly ApplicationDbContext _dbContext; // Penggunaan langsung EF Core untuk model baca

    public GetOrderDetailsQueryHandler(ApplicationDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task<OrderDetailsDto> Handle(GetOrderDetailsQuery request, CancellationToken cancellationToken)
    {
        var orderDto = await _dbContext.Orders
           .Where(o => o.Id == request.OrderId)
           .Select(o => new OrderDetailsDto
            {
                OrderId = o.Id,
                CreationDate = o.CreationDate,
                Status = o.Status.ToString(),
                TotalAmount = o.Items.Sum(item => item.Quantity * item.UnitPriceAmount),
                Items = o.Items.Select(item => new OrderDetailsDto.OrderItemDto
                {
                    ItemName = item.ItemName,
                    Quantity = item.Quantity,
                    UnitPrice = item.UnitPriceAmount
                }).ToList()
            })
           .AsNoTracking() // Penting untuk kueri agar tidak melacak perubahan
           .FirstOrDefaultAsync(cancellationToken);

        if (orderDto == null) throw new OrderNotFoundException(request.OrderId);
        return orderDto;
    }
}

// DTOs (dalam YourApp.Application.DTOs)
public class OrderDetailsDto
{
    public Guid OrderId { get; set; }
    public DateTime CreationDate { get; set; }
    public string Status { get; set; }
    public decimal TotalAmount { get; set; }
    public List<OrderItemDto> Items { get; set; } = new();

    public class OrderItemDto
    {
        public string ItemName { get; set; }
        public int Quantity { get; set; }
        public decimal UnitPrice { get; set; }
    }
}



Mengintegrasikan CQRS dengan Peristiwa Domain

Perintah sering memicu peristiwa domain di dalam agregat.17 Peristiwa domain ini kemudian dapat diproses oleh handler internal (misalnya, menggunakan pola notifikasi MediatR atau
DomainEvents.Raise) untuk melakukan efek samping atau memperbarui model baca.17 Ini memungkinkan handler perintah untuk fokus pada modifikasi keadaan agregat, sementara handler peristiwa menangani konsekuensinya.

Tabel: Perintah CQRS vs. Kueri

Fitur
Perintah (Commands)
Kueri (Queries)
Tujuan
Mengubah keadaan sistem (menulis data).
Mengambil data dari sistem (membaca data).
Efek Samping
Memiliki efek samping (side effects) pada keadaan sistem.
Tidak memiliki efek samping; hanya mengembalikan data.
Tipe Pengembalian
Biasanya void, Task, atau ID entitas yang dibuat.
Mengembalikan Data Transfer Object (DTO) yang dioptimalkan untuk tampilan.
Logika Bisnis
Mengandung logika bisnis kompleks dan validasi domain.
Tidak mengandung logika bisnis atau validasi domain.
Model Data
Berinteraksi dengan model tulis (agregat, entitas domain).
Berinteraksi dengan model baca (seringkali denormalisasi, dioptimalkan untuk kueri).
Skalabilitas
Dapat diskalakan secara independen, seringkali pada lebih sedikit instance untuk menghindari konflik.
Dapat diskalakan secara independen, seringkali pada lebih banyak instance untuk menangani volume kueri tinggi.
Contoh
CreateOrderCommand, UpdateProductPriceCommand, ProcessPaymentCommand.
GetProductDetailsQuery, SearchCustomersQuery, GetOrderHistoryQuery.


Arsitektur Berbasis Peristiwa dan Peristiwa Integrasi

Arsitektur Berbasis Peristiwa (Event-Driven Architecture - EDA) adalah paradigma di mana komponen berkomunikasi melalui peristiwa. Ini sangat penting untuk sistem terdistribusi dan microservices.

Memanfaatkan Peristiwa Domain untuk Komunikasi Internal

Peristiwa Domain bersifat internal untuk satu bounded context.17 Mereka dipicu oleh entitas domain atau agregat untuk memberi sinyal perubahan keadaan.17 Mereka ditangani oleh handler peristiwa domain untuk memicu efek samping atau memperbarui model baca lokal.17 Contohnya adalah
OrderPaidEvent yang memicu UpdateReportingModelHandler internal.

Mengimplementasikan Peristiwa Integrasi untuk Komunikasi Lintas Bounded Context (misalnya, Pola Outbox)

Peristiwa Integrasi mengomunikasikan perubahan antar bounded context atau microservices yang berbeda.31 Mereka biasanya diterbitkan ke message broker (misalnya, RabbitMQ, Kafka).31
Pola Outbox: Ini adalah pola krusial untuk penerbitan peristiwa yang andal dalam sistem terdistribusi, mengatasi "masalah dual write".31 Masalah dual write muncul ketika aplikasi perlu mempertahankan data ke database dan mengirim pesan ke antrean, dan kedua operasi harus berhasil atau gagal bersama untuk menjaga konsistensi.32
Pola Outbox memastikan atomisitas: perubahan data bisnis dan pembuatan peristiwa disimpan dalam satu transaksi database tunggal.32 Sebuah layanan latar belakang terpisah (misalnya,
IHostedService di ASP.NET Core) secara berkala memeriksa tabel "outbox" untuk peristiwa yang belum diproses dan memublikasikannya ke message broker.32 Ini adalah pola desain fundamental untuk mencapai konsistensi transaksional dan keandalan dalam sistem terdistribusi berbasis peristiwa. Dalam dunia di mana transaksi terdistribusi langsung (misalnya, two-phase commit di seluruh database dan message broker) sebagian besar dihindari karena kompleksitas dan overhead kinerja, Pola Outbox menyediakan alternatif yang pragmatis dan kuat. Dengan memastikan bahwa perubahan data bisnis dan pembuatan peristiwa adalah unit atomik dalam
satu transaksi database tunggal, ini menghilangkan "masalah dual write" dan menjamin bahwa peristiwa tidak pernah hilang, bahkan jika message broker eksternal sementara tidak tersedia. Pola ini menggeser beban jaminan pengiriman dari transaksi terdistribusi yang kompleks ke transaksi database lokal yang lebih sederhana dan lebih kuat yang dikombinasikan dengan proses latar belakang asinkron. Ini secara langsung memengaruhi toleransi kesalahan dan skalabilitas sistem, memungkinkan respons pengguna langsung sementara efek samping kompleks ditangani secara andal di latar belakang.
Manfaat Pola Outbox meliputi atomisitas, kinerja (respons instan), keandalan (mekanisme coba ulang), skalabilitas, dan decoupling.32 Pertimbangan penting saat menggunakan pola ini termasuk idempotensi konsumen (karena peristiwa mungkin dikirim beberapa kali), antrean dead letter untuk peristiwa yang gagal secara konsisten, dan pembersihan tabel outbox secara teratur.32

C#


// Dalam YourApp.Infrastructure.Data.Models
// Model untuk tabel outbox di database yang sama dengan data bisnis
public class OutBoxEvent
{
    public Guid Id { get; set; }
    public string EventType { get; set; } // Nama tipe lengkap dari peristiwa integrasi
    public string EventData { get; set; } // Payload peristiwa yang diserialisasi sebagai JSON
    public DateTime CreatedAt { get; set; }
    public bool IsProcessed { get; set; }
    public DateTime? ProcessedAt { get; set; }
    public int RetryCount { get; set; }
}

// Dalam YourApp.Application.IntegrationEvents (atau proyek Kontrak bersama)
// Ini adalah peristiwa yang akan diterbitkan ke bounded context lain atau layanan eksternal
public record OrderCompletedIntegrationEvent(Guid OrderId, decimal TotalAmount, string CustomerEmail);
public record OrderShippedIntegrationEvent(Guid OrderId, DateTime ShippingDate);

// Dalam YourApp.Application.Services atau Command Handler (tempat transaksi bisnis terjadi)
public class OrderProcessingService
{
    private readonly IOrderRepository _orderRepository;
    private readonly ApplicationDbContext _dbContext; // Digunakan untuk transaksi database

    public OrderProcessingService(IOrderRepository orderRepository, ApplicationDbContext dbContext)
    {
        _orderRepository = orderRepository;
        _dbContext = dbContext;
    }

    public async Task CompleteOrderAsync(Guid orderId)
    {
        using var transaction = await _dbContext.Database.BeginTransactionAsync();
        try
        {
            var order = await _orderRepository.GetByIdAsync(orderId);
            if (order == null) throw new OrderNotFoundException(orderId);

            //... logika bisnis untuk menyelesaikan pesanan...
            order.ConfirmPayment(order.TotalAmount); // Asumsi TotalAmount sudah tersedia

            await _orderRepository.UpdateAsync(order); // Pertahankan perubahan pesanan

            // Buat dan simpan peristiwa Outbox dalam transaksi yang sama
            var integrationEvent = new OrderCompletedIntegrationEvent(order.Id, order.TotalAmount, "customer@example.com"); // Email dummy
            var outboxEvent = new OutBoxEvent
            {
                Id = Guid.NewGuid(),
                EventType = integrationEvent.GetType().AssemblyQualifiedName, // Nama tipe lengkap
                EventData = System.Text.Json.JsonSerializer.Serialize(integrationEvent),
                CreatedAt = DateTime.UtcNow,
                IsProcessed = false,
                RetryCount = 0
            };
            _dbContext.OutBoxEvents.Add(outboxEvent);

            await _dbContext.SaveChangesAsync(); // Simpan pesanan dan peristiwa outbox secara atomik
            await transaction.CommitAsync();
        }
        catch (Exception ex)
        {
            await transaction.RollbackAsync(); // Jika ada yang gagal, keduanya di-rollback
            // Log error
            throw;
        }
    }

    public async Task ShipOrderAsync(Guid orderId)
    {
        using var transaction = await _dbContext.Database.BeginTransactionAsync();
        try
        {
            var order = await _orderRepository.GetByIdAsync(orderId);
            if (order == null) throw new OrderNotFoundException(orderId);

            order.ShipOrder(); // Logika domain untuk pengiriman

            await _orderRepository.UpdateAsync(order);

            var integrationEvent = new OrderShippedIntegrationEvent(order.Id, DateTime.UtcNow);
            var outboxEvent = new OutBoxEvent
            {
                Id = Guid.NewGuid(),
                EventType = integrationEvent.GetType().AssemblyQualifiedName,
                EventData = System.Text.Json.JsonSerializer.Serialize(integrationEvent),
                CreatedAt = DateTime.UtcNow,
                IsProcessed = false,
                RetryCount = 0
            };
            _dbContext.OutBoxEvents.Add(outboxEvent);

            await _dbContext.SaveChangesAsync();
            await transaction.CommitAsync();
        }
        catch (Exception ex)
        {
            await transaction.RollbackAsync();
            throw;
        }
    }
}

// Dalam YourApp.Infrastructure.BackgroundServices
// Layanan latar belakang untuk memproses peristiwa outbox
public class OutboxProcessor : BackgroundService
{
    private readonly IServiceProvider _serviceProvider;
    private readonly ILogger<OutboxProcessor> _logger;

    public OutboxProcessor(IServiceProvider serviceProvider, ILogger<OutboxProcessor> logger)
    {
        _serviceProvider = serviceProvider;
        _logger = logger;
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        while (!stoppingToken.IsCancellationRequested)
        {
            await ProcessOutBoxEventsAsync();
            await Task.Delay(TimeSpan.FromSeconds(5), stoppingToken); // Polling setiap 5 detik
        }
    }

    private async Task ProcessOutBoxEventsAsync()
    {
        using var scope = _serviceProvider.CreateScope();
        var dbContext = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
        var eventPublisher = scope.ServiceProvider.GetRequiredService<IIntegrationEventPublisher>(); // Penerbit pesan aktual (misalnya, RabbitMQ, Kafka)

        // Ambil peristiwa yang belum diproses dengan batas coba ulang
        var unprocessedEvents = await dbContext.OutBoxEvents
           .Where(e =>!e.IsProcessed && e.RetryCount < 5)
           .OrderBy(e => e.CreatedAt)
           .Take(10) // Proses dalam batch
           .ToListAsync();

        foreach (var outboxEvent in unprocessedEvents)
        {
            try
            {
                var eventType = Type.GetType(outboxEvent.EventType);
                if (eventType == null)
                {
                    _logger.LogError($"Tipe peristiwa {outboxEvent.EventType} tidak ditemukan.");
                    outboxEvent.IsProcessed = true; // Tandai sebagai diproses untuk menghindari pemrosesan ulang tipe tidak valid
                    continue;
                }
                var eventData = System.Text.Json.JsonSerializer.Deserialize(outboxEvent.EventData, eventType);
                await eventPublisher.PublishAsync((dynamic)eventData); // Publikasikan ke message broker

                outboxEvent.IsProcessed = true;
                outboxEvent.ProcessedAt = DateTime.UtcNow;
            }
            catch (Exception ex)
            {
                outboxEvent.RetryCount++;
                _logger.LogWarning(ex, $"Gagal memproses peristiwa outbox {outboxEvent.Id}, coba ulang: {outboxEvent.RetryCount}");
            }
        }
        if (unprocessedEvents.Any())
        {
            await dbContext.SaveChangesAsync(); // Simpan perubahan pada OutBoxEvents (status diproses, jumlah coba ulang)
        }
    }
}

// Dalam YourApp.Infrastructure.Messaging (contoh untuk penerbitan aktual)
public interface IIntegrationEventPublisher
{
    Task PublishAsync<TEvent>(TEvent @event) where TEvent : class;
}

public class RabbitMqEventPublisher : IIntegrationEventPublisher
{
    //... Implementasi spesifik RabbitMQ untuk memublikasikan peristiwa
    private readonly ILogger<RabbitMqEventPublisher> _logger;

    public RabbitMqEventPublisher(ILogger<RabbitMqEventPublisher> logger)
    {
        _logger = logger;
    }

    public Task PublishAsync<TEvent>(TEvent @event) where TEvent : class
    {
        // Serialisasi peristiwa dan publikasikan ke RabbitMQ
        _logger.LogInformation($"Menerbitkan peristiwa integrasi: {typeof(TEvent).Name} - {System.Text.Json.JsonSerializer.Serialize(@event)}");
        // Logika nyata untuk mengirim ke RabbitMQ
        return Task.CompletedTask;
    }
}



Mengekspos Konsep DDD melalui ASP.NET Core Web API

Lapisan Presentasi, khususnya ASP.NET Core Web API, bertanggung jawab untuk mengekspos fungsionalitas aplikasi ke klien eksternal. Penting untuk menjaga lapisan ini tetap tipis dan fokus pada pemetaan data.

Memetakan DTO ke Model Domain

Pengontrol harus menerima Data Transfer Objects (DTO) dari lapisan presentasi.22 DTO ini kemudian dipetakan ke model domain (entitas/objek nilai) sebelum diteruskan ke lapisan aplikasi.19 Demikian pula, model domain yang diambil dari lapisan aplikasi dipetakan kembali ke DTO untuk respons API.19 AutoMapper adalah pustaka populer untuk pemetaan ini.13 Praktik terbaik menyarankan DTO terpisah untuk
setiap endpoint atau skenario, bahkan jika awalnya terlihat identik, untuk memungkinkan evolusi independen.19

C#


// Dalam YourApp.Api.Controllers
[ApiController]
")]
public class OrdersController : ControllerBase
{
    private readonly IMediator _mediator; // Menggunakan MediatR untuk perintah/kueri
    private readonly IMapper _mapper; // Untuk pemetaan DTO ke Perintah/Kueri

    public OrdersController(IMediator mediator, IMapper mapper)
    {
        _mediator = mediator;
        _mapper = mapper;
    }

    [HttpPost("place")]
   
   
    public async Task<IActionResult> PlaceOrder( PlaceOrderRequestDto requestDto)
    {
        var command = _mapper.Map<PlaceOrderCommand>(requestDto);
        var orderId = await _mediator.Send(command);
        return CreatedAtAction(nameof(GetOrderById), new { id = orderId }, new { OrderId = orderId });
    }

    [HttpGet("{id}")]
   
   
    public async Task<IActionResult> GetOrderById(Guid id)
    {
        var query = new GetOrderDetailsQuery { OrderId = id };
        var orderDto = await _mediator.Send(query);
        if (orderDto == null) return NotFound();
        return Ok(orderDto);
    }

    [HttpPost("{id}/items")]
   
   
   
    public async Task<IActionResult> AddItemToOrder(Guid id, AddItemToOrderRequestDto requestDto)
    {
        var command = new AddItemToOrderCommand
        {
            OrderId = id,
            ProductId = requestDto.ProductId,
            Quantity = requestDto.Quantity
        };
        await _mediator.Send(command);
        return Ok();
    }
}

// Dalam YourApp.Api.DTOs
public class PlaceOrderRequestDto
{
    public Guid CustomerId { get; set; }
    public Dictionary<Guid, int> ProductQuantities { get; set; }
}

public class AddItemToOrderRequestDto
{
    public Guid ProductId { get; set; }
    public int Quantity { get; set; }
}

// Dalam YourApp.Api.Mappings (Profil AutoMapper)
public class ApiMappingProfile : Profile
{
    public ApiMappingProfile()
    {
        // Mapping dari DTO API ke Command Aplikasi
        CreateMap<PlaceOrderRequestDto, PlaceOrderCommand>();
        CreateMap<AddItemToOrderRequestDto, AddItemToOrderCommand>();

        // Mapping dari DTO Aplikasi ke DTO API (jika ada perbedaan)
        // Misalnya, jika OrderDetailsDto dari Application memiliki properti yang tidak perlu diekspos di API
        // CreateMap<Application.DTOs.OrderDetailsDto, Api.DTOs.OrderDetailsResponseDto>();
    }
}



Desain Pengontrol dan Interaksi dengan Lapisan Aplikasi

Pengontrol harus tetap tipis, terutama menangani permintaan HTTP, memetakan DTO, memanggil layanan lapisan aplikasi atau perintah/kueri, dan mengembalikan respons HTTP yang sesuai.22 Mereka tidak boleh mengandung logika bisnis langsung atau logika akses data.22 Interaksi biasanya dilakukan dengan layanan aplikasi atau
IMediator MediatR.26

5. Pola DDD Ideal dan Penerapan Praktisnya

Penerapan DDD yang "ideal" bukanlah solusi satu ukuran untuk semua, melainkan keputusan pragmatis yang didasarkan pada kompleksitas inheren domain bisnis. Ini melibatkan pemilihan pola strategis dan taktis yang tepat untuk mengelola kompleksitas pada berbagai tingkatan.

Pola Strategis untuk Dekomposisi Sistem

Pola strategis DDD berfokus pada pembagian sistem kompleks menjadi area domain yang jelas, dengan penekanan pada demarkasi, interoperabilitas, dan skalabilitas.6
Bounded Contexts (BCs): Ini adalah pola strategis yang paling krusial. Identifikasi batasan logis dalam domain bisnis di mana model dan ubiquitous language konsisten.1 Ini adalah langkah pertama dalam dekomposisi sistem yang kompleks. Konsep Bounded Contexts adalah tentang mengelola kompleksitas dan memungkinkan skalabilitas dalam gaya arsitektur apa pun, termasuk monolit modular. Kemampuan untuk mendefinisikan modul yang jelas dan terisolasi berarti bahwa bahkan dalam satu unit deployment, tim pengembangan dapat bekerja secara otonom pada domain masing-masing, mengurangi overhead koordinasi dan memungkinkan evolusi fitur secara independen. Modularitas ini merupakan prasyarat untuk menskalakan tim pengembangan dan, jika diperlukan, kemudian beralih ke microservices dengan lebih sedikit gesekan. DDD menyediakan kerangka konseptual untuk dekomposisi, terlepas dari deployment fisik.35
Pola Pemetaan Konteks (dari Eric Evans): Pola-pola ini mendefinisikan bagaimana berbagai bounded context berhubungan dan berinteraksi.1
Partnership: Dua tim berhasil/gagal bersama, perencanaan terkoordinasi.1
Shared Kernel: Subset eksplisit dari model domain yang disepakati untuk dibagikan, dijaga agar tetap kecil.1
Customer/Supplier Development: Hubungan upstream-downstream yang jelas, dengan satu tim bertindak sebagai pelanggan dan yang lain sebagai pemasok.1
Conformist: Sistem downstream menyesuaikan diri dengan model upstream, menyederhanakan integrasi.1
Anticorruption Layer (ACL): Membuat lapisan isolasi untuk menerjemahkan antara model sistem upstream asing dan model domain Anda sendiri.1 Ini sangat penting untuk berintegrasi dengan sistem lama atau layanan eksternal.
Open-host Service: Protokol yang jelas untuk mengakses subsistem Anda sebagai serangkaian layanan, untuk integrasi dengan banyak sistem lain.1
Published Language: Bahasa bersama yang terdokumentasi dengan baik (misalnya, standar pertukaran data) untuk komunikasi antar konteks.1 Sering digunakan dengan Open-Host Service.
Separate Ways: Tidak ada koneksi antar konteks, memungkinkan solusi khusus.1
Big Ball of Mud: Batasan di sekitar sistem yang ada yang tidak memiliki batasan nyata.1
Penerapan: Pola-pola ini memandu arsitektur tingkat tinggi, terutama ketika bergerak menuju microservices atau berintegrasi dengan sistem yang ada.6 Mereka membantu mengelola kompleksitas dengan mendefinisikan tanggung jawab yang jelas dan protokol interaksi antar bagian sistem yang besar.

Pola Taktis untuk Pemodelan Domain

Ini adalah "blok bangunan" untuk mengimplementasikan model domain di dalam bounded context.2
Entitas: Untuk objek dengan identitas dan keadaan yang dapat berubah.1
Objek Nilai: Untuk konsep yang tidak dapat diubah yang diidentifikasi oleh nilainya.2
Agregat & Aggregate Roots: Untuk mengelompokkan entitas dan objek nilai terkait, menegakkan konsistensi transaksional dan invarian melalui AR.2
Factories: Bertanggung jawab untuk membuat agregat atau entitas yang kompleks, terutama ketika logika pembuatan rumit, bergantung pada layanan eksternal, atau melibatkan perilaku polimorfik.1 Factories tidak boleh mengandung logika repositori.3 Mereka dapat berupa konstruktor (sederhana), metode statis (niat jelas, beberapa jalur pembuatan), atau kelas factory khusus (kompleks, dapat digunakan kembali, injeksi dependensi).3

C#


// Dalam YourApp.Domain.Factories
public interface IOrderFactory
{
    Order CreateNewDraftOrder(Guid customerId);
    Order CreateOrderFromCart(Guid customerId, IEnumerable<CartItem> items);
}

public class OrderFactory : IOrderFactory
{
    // Dapat menginjeksi layanan jika diperlukan, misalnya, IProductValidationService
    private readonly IProductRepository _productRepository;

    public OrderFactory(IProductRepository productRepository)
    {
        _productRepository = productRepository;
    }

    public Order CreateNewDraftOrder(Guid customerId)
    {
        // Logika pembuatan kompleks, misalnya, mengatur nilai default, menerapkan aturan bisnis awal
        return new Order(Guid.NewGuid(), DateTime.UtcNow);
    }

    public Order CreateOrderFromCart(Guid customerId, IEnumerable<CartItem> items)
    {
        var order = new Order(Guid.NewGuid(), DateTime.UtcNow);
        foreach (var item in items)
        {
            // Asumsi Product lookup/validation terjadi di tempat lain atau sederhana
            // Dalam skenario nyata, mungkin perlu memvalidasi keberadaan produk atau stok
            var product = _productRepository.GetByIdAsync(item.ProductId).Result; // Hindari.Result di kode async nyata
            if (product == null) throw new ProductNotFoundException(item.ProductId);

            order.AddItem(product, item.Quantity);
        }
        return order;
    }
}

public class CartItem
{
    public Guid ProductId { get; set; }
    public string ProductName { get; set; }
    public decimal UnitPrice { get; set; }
    public int Quantity { get; set; }
}


Repositori: Mengabstraksi akses data untuk agregat, menyediakan metode untuk mengambil dan mempertahankan aggregate root.1
Layanan Domain: Untuk logika domain yang mencakup beberapa agregat atau memerlukan ketergantungan eksternal.3
Peristiwa Domain: Untuk memberi sinyal kejadian signifikan dalam domain untuk decoupling internal dan efek samping.3
Penerapan: Pola-pola ini diterapkan selama DDD taktis untuk membangun model domain yang kaya dan ekspresif yang secara akurat mencerminkan realitas bisnis dan menegakkan aturan.

Kapan Menerapkan Pola Mana untuk Desain Optimal

DDD paling cocok untuk domain bisnis yang kompleks di mana pemahaman logika domain inti adalah yang terpenting.2 Untuk aplikasi CRUD yang lebih sederhana, ini mungkin berlebihan.38 "Ideal" penerapan pola DDD bukanlah solusi satu ukuran untuk semua, melainkan keputusan pragmatis berdasarkan kompleksitas inheren domain bisnis. Sementara DDD menawarkan manfaat besar untuk sistem yang rumit, investasi awal dalam pemodelan, penyempurnaan ubiquitous language, dan implementasi pola dapat memperkenalkan overhead yang tidak perlu dan "boilerplate" 39 untuk aplikasi CRUD yang lebih sederhana. "Praktik terbaik" yang sebenarnya terletak pada pengakuan kapan kompleksitas domain
membenarkan investasi dalam DDD, dan kapan arsitektur yang lebih sederhana dan lebih langsung lebih efisien. Over-engineering dengan DDD dapat menghambat produktivitas dan onboarding.39
Disarankan untuk memulai dengan pendekatan paling sederhana (misalnya, konstruktor untuk pembuatan agregat) dan memperkenalkan pola yang lebih kompleks (seperti Factories) hanya ketika kompleksitas menuntutnya.3 Prioritaskan Ubiquitous Language dan Bounded Contexts terlebih dahulu (DDD strategis) untuk mendefinisikan struktur tingkat tinggi sistem.6 Kemudian, terapkan pola taktis (Entitas, VOs, Agregat) untuk membangun model domain yang kaya di dalam setiap bounded context.2 Gunakan Layanan Domain ketika logika tidak secara alami sesuai dengan agregat tunggal.16 Gunakan Repositori untuk kekhawatiran persistensi, selalu beroperasi pada aggregate root.12 Perkenalkan Peristiwa Domain untuk decoupling internal dan efek samping asinkron.17
Clean Architecture menyediakan kerangka kerja struktural untuk menampung pola DDD ini secara efektif.19 CQRS dan Event-Driven Architecture adalah pola lanjutan yang perlu dipertimbangkan ketika persyaratan skalabilitas, kinerja, atau konsistensi spesifik muncul, terutama dalam sistem terdistribusi.28 Ini menyiratkan evaluasi berkelanjutan terhadap kompleksitas domain yang berkembang. Sebuah sistem mungkin dimulai dengan sederhana, tetapi seiring bertambahnya aturan bisnis, secara bertahap memperkenalkan pola DDD menjadi evolusi alami daripada pemaksaan awal yang berat. Adopsi fleksibel ini menghindari "awal yang sulit" 38 dan memungkinkan tim untuk mendapatkan momentum sebelum mengatasi kompleksitas arsitektur penuh.

6. Trade-off dan Pertimbangan dalam Arsitektur Gabungan

Meskipun Domain-Driven Design (DDD) dan pola arsitektur terkait seperti Clean Architecture, CQRS, dan Event-Driven Architecture menawarkan manfaat signifikan, penerapannya secara bersamaan memperkenalkan serangkaian trade-off dan kompleksitas yang perlu dipertimbangkan dengan cermat.

Peningkatan Kompleksitas dan Kurva Pembelajaran

Menggabungkan DDD dengan Clean Architecture, CQRS, dan pola Event-Driven secara signifikan meningkatkan kompleksitas desain aplikasi.28 Ini menuntut cara berpikir yang berbeda tentang sistem 40 dan dapat menjadi sangat berat pada awalnya, terutama bagi tim yang baru mengenal pola-pola ini.38 Peningkatan boilerplate code terjadi karena banyaknya lapisan, DTO, perintah, kueri, handler, dan definisi peristiwa yang diperlukan.39 Menemukan pengembang yang memenuhi syarat dan akrab dengan pola-pola canggih ini juga bisa menjadi tantangan.40 Peningkatan kompleksitas ini bukan hanya beban teknis tetapi investasi strategis. Meskipun mengarah pada biaya awal yang lebih tinggi dalam hal waktu pengembangan, kurva pembelajaran, dan boilerplate code, investasi ini terbayar secara signifikan dalam jangka panjang untuk sistem yang kompleks dan berkembang. Lapisan dan abstraksi tambahan dirancang untuk meningkatkan pemeliharaan, kemampuan pengujian, dan kemampuan beradaptasi 21, yang sangat penting untuk umur panjang perangkat lunak. Untuk sistem yang lebih sederhana, investasi ini memang "berlebihan" 38, tetapi untuk domain dengan aturan bisnis yang rumit dan frekuensi perubahan yang tinggi, ini berubah menjadi "desain masa depan" 39 yang mengurangi risiko biaya yang mahal.

Implikasi Kinerja dan Skalabilitas

Manfaat:
Skalabilitas Independen: CQRS memungkinkan penskalaan independen dari model baca dan tulis, yang dapat secara signifikan meningkatkan kinerja sistem di bawah beban, terutama ketika jumlah operasi baca lebih besar daripada operasi tulis.28
Skema Data yang Dioptimalkan: Operasi baca dapat menggunakan skema yang dioptimalkan khusus untuk kueri, sementara operasi tulis menggunakan skema yang dioptimalkan untuk pembaruan.28
Pemrosesan Asinkron: Arsitektur berbasis peristiwa memungkinkan operasi berat di-offload ke proses latar belakang asinkron, memberikan respons instan kepada pengguna dan penanganan beban yang lebih baik.17
Mengurangi Konflik Penguncian: Pemisahan baca/tulis dalam CQRS dapat membantu meminimalkan konflik penguncian pada data yang sama.28
Tantangan:
Overhead Sistem Pesan: Mengintegrasikan sistem pesan memperkenalkan tantangan seperti kegagalan pesan, duplikasi, dan kebutuhan akan mekanisme coba ulang.28
"Consumer Lag": Jika peristiwa diproduksi lebih cepat daripada yang dapat dikonsumsi, dapat terjadi backlog yang membebani sistem.43 Ini memerlukan penskalaan konsumen.43
Biaya Rekreasi Keadaan: Dalam Event Sourcing, biaya untuk merekreasi keadaan entitas dengan memutar ulang aliran peristiwa bisa tinggi, terutama untuk aliran peristiwa yang besar.40 Snapshot dapat mengurangi masalah ini.40
Penggunaan Ruang Disk Tinggi: Penyimpanan peristiwa dapat menggunakan banyak ruang disk.40

Tantangan Konsistensi Eventual

Ketika database baca dan tulis dipisahkan (umum dalam CQRS + Event Sourcing), data di database baca mungkin tidak segera mencerminkan perubahan terbaru yang dilakukan pada database tulis.28 Penundaan ini, yang disebut
konsistensi eventual, dapat membingungkan pengguna.30 Ini memerlukan desain yang cermat untuk mendeteksi dan menangani skenario di mana pengguna bertindak berdasarkan data yang usang.28 Konsistensi eventual ini bukan cacat melainkan pilihan desain yang disengaja untuk mencapai kinerja dan ketersediaan yang lebih tinggi. Ini membutuhkan pertimbangan cermat terhadap pengalaman pengguna dan mekanisme yang kuat untuk sinkronisasi.
Mitigasi termasuk "tampilan optimis" di UI (menampilkan hasil seolah-olah berhasil segera setelah perintah dikirim, lalu memperbarui jika ada kegagalan), memberi tahu pengguna tentang pembaruan yang tertunda, atau menggunakan mekanisme seperti mengembalikan ID urutan peristiwa untuk memastikan kueri berikutnya mencerminkan perubahan.30 Sistem harus dirancang untuk memperhitungkan konsistensi eventual dalam skenario ini.41

Boilerplate Code dan Pemeliharaan

Arsitektur gabungan dapat meningkatkan jumlah proyek, kelas, antarmuka, dan pemetaan (DTO, perintah, kueri).39 Ini dapat menyebabkan "pengontrol gemuk" atau "model gemuk" jika tidak dikelola dengan baik.38 Diperlukan disiplin untuk menjaga pemisahan kekhawatiran dan menghindari "model domain anemic".38 Debugging bisa menjadi lebih menantang dalam sistem yang sangat didekopel dan berbasis peristiwa karena alur kerja terdistribusi dan komunikasi asinkron.38 Melacak seluruh proses dari awal hingga akhir bisa jadi sulit.43

Dampak pada Pengujian Unit (XUnit, Moq)

Manfaat:
Clean Architecture dan DDD secara alami mempromosikan kode yang dapat diuji karena pemisahan kekhawatiran yang jelas dan inversi dependensi.20
Pengujian unit cepat, terisolasi, dapat diulang, dan dapat memeriksa sendiri.46
Logika domain dan aplikasi dapat diuji secara terpisah tanpa ketergantungan eksternal seperti database atau server web.20
Tantangan/Praktik Terbaik:
Menguji Lapisan Domain (Entitas, Objek Nilai, Agregat): Uji perilaku dan invarian yang dienkapsulasi dalam entitas dan aggregate root secara langsung. Objek nilai, karena tidak dapat diubah, mudah diuji untuk kesetaraan dan perilaku. Contoh: Uji Order.AddItem() untuk memastikan kuantitas diperbarui atau item baru ditambahkan dengan benar, dan Order.ConfirmPayment() untuk memverifikasi perubahan status dan aturan pembayaran.
Menguji Lapisan Aplikasi (Command/Query Handlers, Layanan Domain): Lapisan-lapisan ini mengorkestrasi logika domain dan berinteraksi dengan repositori/layanan eksternal. Gunakan kerangka kerja mocking seperti Moq (atau NSubstitute) untuk meng-mock dependensi (repositori, layanan eksternal, MediatR).19 Ikuti pola Arrange-Act-Assert (AAA).46 Beri nama pengujian secara deskriptif (
MethodName_GivenScenario_ShouldExpectedResult).46 Hindari penggunaan mock yang berlebihan; gunakan dependensi nyata jika sesuai.48 Contoh: Uji
AddItemCommandHandler dengan meng-mock IOrderRepository dan IProductRepository.47

C#


// Dalam YourApp.Application.Tests
public class AddItemToOrderCommandHandlerTests
{
    private readonly Mock<IOrderRepository> _mockOrderRepository;
    private readonly Mock<IProductRepository> _mockProductRepository;
    private readonly AddItemToOrderCommandHandler _handler;

    public AddItemToOrderCommandHandlerTests()
    {
        _mockOrderRepository = new Mock<IOrderRepository>();
        _mockProductRepository = new Mock<IProductRepository>();
        _handler = new AddItemToOrderCommandHandler(_mockOrderRepository.Object, _mockProductRepository.Object);
    }

    [Fact]
    public async Task Handle_GivenValidCommand_ShouldAddItemAndReturnOrderId()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var productId = Guid.NewGuid();
        var quantity = 2;
        var command = new AddItemToOrderCommand { OrderId = orderId, ProductId = productId, Quantity = quantity };

        var existingOrder = new Order(orderId, DateTime.UtcNow);
        var product = new Product(productId, "Test Product", new Money(10.0M, "USD"));

        _mockOrderRepository.Setup(r => r.GetByIdAsync(orderId)).ReturnsAsync(existingOrder);
        _mockProductRepository.Setup(r => r.GetByIdAsync(productId)).ReturnsAsync(product);
        _mockOrderRepository.Setup(r => r.UpdateAsync(It.IsAny<Order>())).Returns(Task.CompletedTask);

        // Act
        var result = await _handler.Handle(command, CancellationToken.None);

        // Assert
        Assert.Equal(orderId, result);
        _mockOrderRepository.Verify(r => r.UpdateAsync(It.Is<Order>(o => o.Items.Count == 1 && o.Items.First().ProductId == productId && o.Items.First().Quantity == quantity)), Times.Once);
    }

    [Fact]
    public async Task Handle_GivenNonExistingOrder_ShouldThrowOrderNotFoundException()
    {
        // Arrange
        var command = new AddItemToOrderCommand { OrderId = Guid.NewGuid(), ProductId = Guid.NewGuid(), Quantity = 1 };
        _mockOrderRepository.Setup(r => r.GetByIdAsync(It.IsAny<Guid>())).ReturnsAsync((Order)null);

        // Act & Assert
        await Assert.ThrowsAsync<OrderNotFoundException>(() => _handler.Handle(command, CancellationToken.None));
        _mockOrderRepository.Verify(r => r.UpdateAsync(It.IsAny<Order>()), Times.Never);
    }

    [Fact]
    public async Task Handle_GivenNonExistingProduct_ShouldThrowProductNotFoundException()
    {
        // Arrange
        var orderId = Guid.NewGuid();
        var command = new AddItemToOrderCommand { OrderId = orderId, ProductId = Guid.NewGuid(), Quantity = 1 };
        var existingOrder = new Order(orderId, DateTime.UtcNow);

        _mockOrderRepository.Setup(r => r.GetByIdAsync(orderId)).ReturnsAsync(existingOrder);
        _mockProductRepository.Setup(r => r.GetByIdAsync(It.IsAny<Guid>())).ReturnsAsync((Product)null);

        // Act & Assert
        await Assert.ThrowsAsync<ProductNotFoundException>(() => _handler.Handle(command, CancellationToken.None));
        _mockOrderRepository.Verify(r => r.UpdateAsync(It.IsAny<Order>()), Times.Never);
    }
}



Praktik Terbaik Penanganan Kesalahan Global

Masalah: Kebocoran stack trace dan detail pengecualian internal ke klien.52 Respons kesalahan yang tidak konsisten.

Tujuan: Menangkap dan mencatat pengecualian yang tidak tertangani, mengembalikan respons ProblemDetails yang terstruktur, konsisten, dan aman.52
Pendekatan:
Middleware Kustom (UseExceptionHandler): Pendekatan tradisional yang menangkap dan mencatat pengecualian yang tidak tertangani, mengeksekusi ulang permintaan dalam pipeline alternatif (misalnya, jalur /Error).55 Dapat mengatur kode status dan menulis respons kustom.54 Tempatkan di awal pipeline.53

C#


// Dalam YourApp.Api.Middlewares
public class GlobalExceptionHandlerMiddleware : IMiddleware
{
    private readonly ILogger<GlobalExceptionHandlerMiddleware> _logger;
    private readonly IHostEnvironment _env;

    public GlobalExceptionHandlerMiddleware(ILogger<GlobalExceptionHandlerMiddleware> logger, IHostEnvironment env)
    {
        _logger = logger;
        _env = env;
    }

    public async Task InvokeAsync(HttpContext context, RequestDelegate next)
    {
        try
        {
            await next(context);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Terjadi pengecualian yang tidak tertangani.");
            context.Response.ContentType = "application/problem+json";
            context.Response.StatusCode = StatusCodes.Status500InternalServerError; // Default ke 500

            var problemDetails = new ProblemDetails
            {
                Status = context.Response.StatusCode,
                Title = "Terjadi kesalahan saat memproses permintaan Anda.",
                Detail = _env.IsDevelopment()? ex.ToString() : "Terjadi kesalahan server internal yang tidak terduga.",
                Instance = context.Request.Path
            };

            await context.Response.WriteAsJsonAsync(problemDetails);
        }
    }
}

// Dalam Program.cs
// builder.Services.AddTransient<GlobalExceptionHandlerMiddleware>();
// app.UseMiddleware<GlobalExceptionHandlerMiddleware>(); // Tempatkan di awal pipeline


IExceptionHandler (Modern.NET 8+): Direkomendasikan untuk proyek baru.52 Memungkinkan handler yang berfokus untuk tipe pengecualian spesifik.54
Implementasikan antarmuka IExceptionHandler.53
Gunakan TryHandleAsync untuk memeriksa tipe pengecualian, menanganinya, dan mengembalikan true (ditangani) atau false (teruskan ke handler berikutnya).53
Memanfaatkan IProblemDetailsService: Menstandardisasi respons kesalahan sesuai dengan RFC 9457 (Problem Details).52
Daftarkan builder.Services.AddProblemDetails();.53
Injeksi IProblemDetailsService ke dalam handler Anda.54
Menangani Pengecualian Spesifik (misalnya, ValidationException):
Buat implementasi IExceptionHandler spesifik (misalnya, ValidationExceptionHandler).53
Daftarkan handler spesifik sebelum yang umum.53

C#


// Dalam YourApp.Api.Handlers (atau proyek ErrorHandling khusus)
public class GlobalExceptionHandler(
    IProblemDetailsService problemDetailsService,
    ILogger<GlobalExceptionHandler> logger,
    IHostEnvironment env) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext httpContext,
        Exception exception,
        CancellationToken cancellationToken)
    {
        logger.LogError(exception, "Terjadi pengecualian yang tidak tertangani.");

        httpContext.Response.StatusCode = StatusCodes.Status500InternalServerError;
        // Sesuaikan ProblemDetails berdasarkan lingkungan/tipe pengecualian
        var problemDetails = new ProblemDetails
        {
            Status = httpContext.Response.StatusCode,
            Title = "Terjadi kesalahan yang tidak terduga.",
            Detail = env.IsDevelopment()? exception.ToString() : "Terjadi kesalahan server internal.",
            Instance = httpContext.Request.Path
        };

        return await problemDetailsService.TryWriteAsync(new ProblemDetailsContext
        {
            HttpContext = httpContext,
            Exception = exception,
            ProblemDetails = problemDetails
        });
    }
}

public class ValidationException : Exception // Contoh kelas pengecualian validasi
{
    public List<ValidationError> Errors { get; } = new List<ValidationError>();
    public ValidationException(string message, IEnumerable<ValidationError> errors) : base(message)
    {
        Errors.AddRange(errors);
    }
}

public class ValidationError
{
    public string PropertyName { get; set; }
    public string ErrorMessage { get; set; }
}

public class ValidationExceptionHandler(
    IProblemDetailsService problemDetailsService,
    ILogger<ValidationExceptionHandler> logger) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext httpContext,
        Exception exception,
        CancellationToken cancellationToken)
    {
        if (exception is not ValidationException validationException)
        {
            return false; // Tidak ditangani oleh handler spesifik ini
        }

        logger.LogWarning(validationException, "Terjadi kesalahan validasi.");

        httpContext.Response.StatusCode = StatusCodes.Status400BadRequest;

        var problemDetails = new ProblemDetails
        {
            Status = StatusCodes.Status400BadRequest,
            Title = "Terjadi satu atau lebih kesalahan validasi.",
            Detail = "Silakan periksa bidang 'errors' untuk detailnya.",
            Instance = httpContext.Request.Path
        };

        var errors = validationException.Errors
           .GroupBy(e => e.PropertyName)
           .ToDictionary(
                g => g.Key.ToLowerInvariant(),
                g => g.Select(e => e.ErrorMessage).ToArray()
            );
        problemDetails.Extensions.Add("errors", errors);

        return await problemDetailsService.TryWriteAsync(new ProblemDetailsContext
        {
            HttpContext = httpContext,
            Exception = exception,
            ProblemDetails = problemDetails
        });
    }
}

// Dalam Program.cs
// builder.Services.AddProblemDetails(); // Diperlukan untuk IProblemDetailsService
// builder.Services.AddExceptionHandler<ValidationExceptionHandler>(); // Handler spesifik terlebih dahulu
// builder.Services.AddExceptionHandler<GlobalExceptionHandler>();    // Handler fallback umum
// app.UseExceptionHandler(); // Tambahkan ke pipeline



Tabel: Trade-off Arsitektur Gabungan

Pola/Kombinasi
Manfaat
Trade-off/Kompleksitas
Mitigasi/Pertimbangan
DDD + Clean Architecture
Pemisahan kekhawatiran yang kuat, inti bisnis yang stabil, kemampuan pengujian tinggi, fleksibilitas perubahan teknologi.
Peningkatan kompleksitas awal, boilerplate code, kurva pembelajaran yang lebih curam.
Mulai dengan sederhana, perkenalkan pola secara bertahap, investasi dalam pelatihan tim, gunakan alat bantu (AutoMapper, MediatR).
CQRS
Skalabilitas baca/tulis independen, skema data yang dioptimalkan, kinerja yang lebih baik untuk sistem read-heavy, pemisahan kekhawatiran yang jelas.
Peningkatan kompleksitas desain, tantangan perpesanan (duplikasi, coba ulang), konsistensi eventual.
Gunakan pola Outbox untuk penerbitan peristiwa yang andal, pastikan konsumen bersifat idempotensi, pertimbangkan "tampilan optimis" di UI, pantau lag konsumen.
Event-Driven Architecture
Decoupling antar komponen, skalabilitas, responsivitas real-time, audit trail historis (dengan Event Sourcing).
Kompleksitas debugging, konsistensi eventual, tantangan versioning peristiwa, penggunaan ruang disk yang tinggi (Event Sourcing).
Gunakan Pola Outbox, pastikan konsumen bersifat idempotensi, desain peristiwa dengan cermat (hindari peristiwa generik besar), gunakan snapshot untuk Event Sourcing.
Integrasi Keseluruhan
Sistem yang sangat skalabel, maintainable, dan responsif yang selaras dengan domain bisnis.
Kompleksitas yang signifikan, membutuhkan tim yang sangat terampil, biaya pengembangan awal yang lebih tinggi.
Adopsi bertahap, fokus pada domain inti yang kompleks, investasi berkelanjutan dalam arsitektur dan praktik terbaik, evaluasi nilai bisnis vs. kompleksitas.


Tabel: Strategi Penanganan Kesalahan Global dalam ASP.NET Core

Strategi
Kapan Digunakan
Kelebihan
Kekurangan
Developer Exception Page
Hanya di lingkungan pengembangan (IsDevelopment()).
Memberikan informasi detail (stack trace, kueri, header) untuk debugging.
Tidak cocok untuk produksi; mengekspos detail sensitif.
UseExceptionHandler Middleware
Lingkungan non-pengembangan.
Menangkap dan mencatat pengecualian yang tidak tertangani, dapat mengarahkan ke halaman kesalahan generik, dapat mengembalikan respons kustom.
Bisa menjadi kompleks dengan banyak aturan pengecualian spesifik, memerlukan serialisasi respons manual, kurang modular.
IExceptionHandler + ProblemDetails
Direkomendasikan untuk semua lingkungan, terutama produksi, di.NET 8+.
Pendekatan modern, modular, dapat diuji; memungkinkan handler spesifik untuk tipe pengecualian tertentu; respons kesalahan terstandardisasi (RFC 9457); dapat dirantai.
Membutuhkan.NET 8+; kurva pembelajaran awal untuk konsep IExceptionHandler dan ProblemDetails.


## 7. Kesimpulan dan Rekomendasi

Penerapan Domain-Driven Design (DDD) dalam proyek ASP.NET Core, terutama ketika dikombinasikan dengan pola arsitektur lanjutan seperti Clean Architecture, Pola Repositori, CQRS, dan Arsitektur Berbasis Peristiwa, menawarkan kerangka kerja yang kuat untuk membangun aplikasi perusahaan yang skalabel, maintainable, dan selaras dengan domain bisnis.
Manfaat Utama:
Kejelasan Domain: DDD memaksakan pemahaman mendalam tentang domain bisnis, yang tercermin dalam kode melalui Ubiquitous Language dan Bounded Contexts. Ini menghasilkan sistem yang lebih intuitif dan mudah dipahami oleh pengembang dan ahli domain.2
Modularitas dan Decoupling: Clean Architecture menyediakan struktur yang kuat untuk memisahkan kekhawatiran, memastikan bahwa logika bisnis inti tetap independen dari detail infrastruktur dan UI.21 Pola Repositori mendekopel domain dari mekanisme persistensi 24, sementara Peristiwa Domain mendekopel efek samping dari logika inti.17
Skalabilitas dan Kinerja: CQRS memungkinkan penskalaan independen dari operasi baca dan tulis, mengoptimalkan kinerja untuk beban kerja tertentu.28 Arsitektur Berbasis Peristiwa, terutama dengan Pola Outbox, meningkatkan keandalan dan memungkinkan pemrosesan asinkron, yang penting untuk sistem terdistribusi.32
Kemampuan Pengujian: Pemisahan kekhawatiran yang jelas dalam Clean Architecture dan DDD secara inheren meningkatkan kemampuan pengujian, memungkinkan pengujian unit yang cepat dan terisolasi untuk logika bisnis.46
Tantangan dan Pertimbangan:
Kompleksitas Inherent: Menggabungkan pola-pola ini secara signifikan meningkatkan kompleksitas desain, boilerplate code, dan kurva pembelajaran awal.28 Ini adalah investasi strategis yang membuahkan hasil dalam jangka panjang untuk domain yang kompleks.
Konsistensi Eventual: Dalam sistem CQRS dan Event-Driven, konsistensi eventual adalah trade-off yang perlu dikelola dengan hati-hati, terutama dalam hal pengalaman pengguna.28
Manajemen Overhead: Debugging dan pemeliharaan dapat menjadi lebih rumit karena sifat sistem yang terdistribusi dan asinkron.43
Rekomendasi:
Mulai dengan Domain: Selalu awali dengan memahami domain bisnis secara mendalam dan membangun Ubiquitous Language yang kuat bersama ahli domain. Ini adalah fondasi untuk semua keputusan desain selanjutnya.2
Adopsi Bertahap: Jangan menerapkan semua pola sekaligus. Mulai dengan DDD taktis (Entitas, Objek Nilai, Agregat) dan struktur Clean Architecture dasar. Perkenalkan CQRS, Event-Driven Architecture, atau Pola Outbox hanya ketika kompleksitas domain atau persyaratan kinerja/skalabilitas membenarkannya.36
Prioritaskan Integritas Agregat: Pastikan Aggregate Root secara ketat menegakkan invarian dan menjadi satu-satunya titik masuk untuk modifikasi agregat. Ini adalah kunci untuk menjaga konsistensi data dalam model domain.13
Manfaatkan Abstraksi: Gunakan antarmuka (misalnya, untuk Repositori, Layanan Domain) untuk mendekopel lapisan dan memungkinkan fleksibilitas dalam implementasi. Ini mendukung kemampuan pengujian dan kemampuan beradaptasi di masa depan.23
Desain Peristiwa dengan Cermat: Bedakan antara Peristiwa Domain (internal) dan Peristiwa Integrasi (lintas konteks). Untuk peristiwa integrasi, pertimbangkan Pola Outbox untuk penerbitan yang andal.32
Penanganan Kesalahan yang Robust: Terapkan strategi penanganan kesalahan global yang konsisten menggunakan IExceptionHandler dan ProblemDetails di ASP.NET Core untuk memberikan respons yang aman dan informatif kepada klien.52
Investasi dalam Pengujian: Manfaatkan struktur yang disediakan oleh Clean Architecture dan DDD untuk menulis pengujian unit yang komprehensif menggunakan XUnit dan Moq, memastikan logika bisnis inti berfungsi dengan benar dan terisolasi dari ketergantungan infrastruktur.46
Dengan pendekatan yang terukur dan pemahaman yang kuat tentang trade-off yang terlibat, pengembang dapat secara efektif menerapkan DDD dan pola arsitektur terkait dalam aplikasi ASP.NET Core untuk membangun sistem yang tidak hanya berfungsi tetapi juga tahan lama, mudah diubah, dan mampu berkembang seiring dengan kebutuhan bisnis.
Karya yang dikutip
Domain-driven design - Wikipedia, diakses Agustus 13, 2025, https://en.wikipedia.org/wiki/Domain-driven_design
Domain-Driven Design (DDD) - Redis, diakses Agustus 13, 2025, https://redis.io/glossary/domain-driven-design-ddd/
Domain-Driven Design (DDD) in Enterprise Web Development with ..., diakses Agustus 13, 2025, https://www.faciletechnolab.com/blog/domain-driven-design-ddd-in-enterprise-web-development-with-aspnet-core/
Ubiquitous Language: How to implement it in your code - Platform Engr®, diakses Agustus 13, 2025, https://www.platformengr.com/2023/10/30/how-to-implement-a-ubiquitous-language-in-your-code/
Ubiquitous Language - EDA Visuals - David Boyne, diakses Agustus 13, 2025, https://eda-visuals.boyney.io/visuals/ubiquitous-language
Domain Driven Design (DDD) - Software Architecture Best Practices - Rock the Prototype, diakses Agustus 13, 2025, https://rock-the-prototype.com/en/software-architecture/domain-driven-design-ddd/
Domain analysis for microservices - Azure Architecture Center - Microsoft Learn, diakses Agustus 13, 2025, https://learn.microsoft.com/en-us/azure/architecture/microservices/model/domain-analysis
Do domain driven design and clean architecture always go together? : r/dotnet - Reddit, diakses Agustus 13, 2025, https://www.reddit.com/r/dotnet/comments/1i1b6wj/do_domain_driven_design_and_clean_architecture/
Explain me like I'm 5 what „The bounded context“ means : r/microservices - Reddit, diakses Agustus 13, 2025, https://www.reddit.com/r/microservices/comments/1bms6dh/explain_me_like_im_5_what_the_bounded_context/
When do you use entities, value objects and aggregates (DDD)? - Stack Overflow, diakses Agustus 13, 2025, https://stackoverflow.com/questions/77425208/when-do-you-use-entities-value-objects-and-aggregates-ddd
Entities and Value Objects: Diving Deep into Domain-Driven Design, diakses Agustus 13, 2025, https://www.abrahamberg.com/blog/entities-and-value-objects-diving-deep-into-domain-driven-design/
Implementing the infrastructure persistence layer with Entity Framework Core - .NET, diakses Agustus 13, 2025, https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-implementation-entity-framework-core
Aggregate Design in .NET - Code Maze, diakses Agustus 13, 2025, https://code-maze.com/csharp-design-pattern-aggregate/
Modeling Aggregates with DDD and Entity Framework - Kalele, diakses Agustus 13, 2025, https://kalele.io/modeling-aggregates-with-ddd-and-entity-framework/
Sample DDD structure in C#.NET - Shift Asia, diakses Agustus 13, 2025, https://shiftasia.com/community/sample-ddd-implementation-in-c-net/
Domain Services | ABP.IO Documentation, diakses Agustus 13, 2025, https://abp.io/docs/latest/framework/architecture/domain-driven-design/domain-services
Master Domain Events in C#: Decoupled & Scalable Architecture ..., diakses Agustus 13, 2025, https://www.ronnydelgado.com/my-blog/domain-events-ddd-clean-architecture
domain-events · GitHub Topics, diakses Agustus 13, 2025, https://github.com/topics/domain-events
ardalis/ddd-guestbook: A DDD guestbook example written ... - GitHub, diakses Agustus 13, 2025, https://github.com/ardalis/ddd-guestbook
Clean Architecture in ASP.NET Core - NDepend Blog, diakses Agustus 13, 2025, https://blog.ndepend.com/clean-architecture-for-asp-net-core-solution/
Clean Architecture + DDD + TDD in ASP.NET Core | by Anirudh Rawat | Medium, diakses Agustus 13, 2025, https://medium.com/@anirudhrawat1/%EF%B8%8F-clean-architecture-ddd-tdd-in-asp-net-core-272a5ef104da
Clean Architecture In ASP.NET Core Web API - C# Corner, diakses Agustus 13, 2025, https://www.c-sharpcorner.com/article/clean-architecture-in-asp-net-core-web-api/
Building a Clean ASP.NET Core API with C# 13, EF Core, and DDD - C# Corner, diakses Agustus 13, 2025, https://www.c-sharpcorner.com/article/building-a-clean-asp-net-core-api-with-c-sharp-13-ef-core-and-ddd/
Repository Pattern C# ultimate guide: Entity Framework Core, Clean Architecture, DTOs, Dependency Injection, CQRS - Medium, diakses Agustus 13, 2025, https://medium.com/@codebob75/repository-pattern-c-ultimate-guide-entity-framework-core-clean-architecture-dtos-dependency-6a8d8b444dcb
CQRS And MediatR Pattern Implementation Using .NET Core 6 Web API - C# Corner, diakses Agustus 13, 2025, https://www.c-sharpcorner.com/article/cqrs-and-mediatr-pattern-implementation-using-net-core-6-web-api/
CQRS with MediatR in ASP.NET Core: A Practical Guide to ..., diakses Agustus 13, 2025, https://medium.com/@ulomaobilookenyi/cqrs-with-mediatr-in-asp-net-core-a-practical-guide-to-decoupled-architecture-7398f7eec846
Implementing the CQRS and Mediator pattern in a .NET 8 Web API - Medium, diakses Agustus 13, 2025, https://medium.com/@EdsonMZ/implementing-the-cqrs-and-mediator-pattern-in-a-net-8-web-api-8c0319a4525c
CQRS Pattern - Azure Architecture Center | Microsoft Learn, diakses Agustus 13, 2025, https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs
CQRS and DDD terminology - Software Engineering Stack Exchange, diakses Agustus 13, 2025, https://softwareengineering.stackexchange.com/questions/302808/cqrs-and-ddd-terminology
Introducing DDD/ES/CQRS: how to deal with Eventual consistency in master/detail forms ?, diakses Agustus 13, 2025, https://groups.google.com/g/dddcqrs/c/BRKjDD2hoGg
Event Driven Architecture, diakses Agustus 13, 2025, https://awesome-architecture.com/event-driven-architecture/
OutBox Pattern: Mastering Data Consistency in Distributed Systems ..., diakses Agustus 13, 2025, https://mcuslu.medium.com/outbox-pattern-mastering-data-consistency-in-distributed-systems-with-net-core-9c1a25323225
asp.net core with clean architecture and AutoMapper - Pass DTO through service layer to controller - Stack Overflow, diakses Agustus 13, 2025, https://stackoverflow.com/questions/57309559/asp-net-core-with-clean-architecture-and-automapper-pass-dto-through-service-l
Clean Architecture + CQRS + DDD Building Blocks 9 hours long "mini-course" - Reddit, diakses Agustus 13, 2025, https://www.reddit.com/r/csharp/comments/sk6d17/clean_architecture_cqrs_ddd_building_blocks_9/
Architecting Robust .NET Solutions: Modular Monolithic, Clean ..., diakses Agustus 13, 2025, https://medium.com/@mail2mhossain/architecting-robust-net-dfa4f3725142
Creating Aggregates in DDD: Constructor, Static Method, or Factory? - Medium, diakses Agustus 13, 2025, https://medium.com/@iamprovidence/creating-aggregates-in-ddd-constructor-static-method-or-factory-931aa698aa4a
c# - What methods should go in my DDD factory class? - Stack Overflow, diakses Agustus 13, 2025, https://stackoverflow.com/questions/610965/what-methods-should-go-in-my-ddd-factory-class
What I learned from using Event Driven Architecture and DDD | by Adam Skołuda - Medium, diakses Agustus 13, 2025, https://medium.com/briisk/what-i-learned-from-using-event-driven-architecture-and-ddd-ab154eeba489
Clean Architecture & DDD Vs. Pragmatism — Efficiency Without Overengineering - Medium, diakses Agustus 13, 2025, https://medium.com/towardsdev/clean-architecture-ddd-vs-pragmatism-efficiency-without-overengineering-9c3efde06f4b
What are the disadvantages of using Event sourcing and CQRS? - Stack Overflow, diakses Agustus 13, 2025, https://stackoverflow.com/questions/33279680/what-are-the-disadvantages-of-using-event-sourcing-and-cqrs
Event Sourcing pattern - Azure Architecture Center | Microsoft Learn, diakses Agustus 13, 2025, https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing
Crafting Maintainable Python Applications with Domain-Driven Design and Clean Architecture - ThinhDA, diakses Agustus 13, 2025, https://thinhdanggroup.github.io/python-code-structure/
Event-Driven Architecture Issues & Challenges - CodeOpinion, diakses Agustus 13, 2025, https://codeopinion.com/event-driven-architecture-issues-challenges/
Entity/Domain purety dilemma in the clean architecutre/Domain driven design - Stack Overflow, diakses Agustus 13, 2025, https://stackoverflow.com/questions/73111031/entity-domain-purety-dilemma-in-the-clean-architecutre-domain-driven-design
Event-Driven Architecture: The Hard Parts | Three Dots Labs blog, diakses Agustus 13, 2025, https://threedots.tech/episode/event-driven-architecture/
Best practices for writing unit tests - .NET - Microsoft Learn, diakses Agustus 13, 2025, https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices
Unit Testing Clean Architecture Use Cases - Milan Jovanović, diakses Agustus 13, 2025, https://www.milanjovanovic.tech/blog/unit-testing-clean-architecture-use-cases
How do you best prepare for writing solid unit and integration tests in C#? : r/dotnet - Reddit, diakses Agustus 13, 2025, https://www.reddit.com/r/dotnet/comments/1it1eqq/how_do_you_best_prepare_for_writing_solid_unit/
Implementation of Unit Test using Xunit and Moq in .NET Core 6 Web API | by Jaydeep Patil, diakses Agustus 13, 2025, https://medium.com/@jaydeepvpatil225/implementation-of-unit-test-using-xunit-and-moq-in-net-core-6-web-api-539205f1d38f
Implementing Unit Test .Net Core Application Using CQRS Handler - C# Corner, diakses Agustus 13, 2025, https://www.c-sharpcorner.com/article/implementing-unit-test-net-core-application-using-cqrs-handler/
MediatR: How to Quickly Test Your Handlers with Unit Tests - Goat Review, diakses Agustus 13, 2025, https://goatreview.com/mediatr-quickly-test-handlers-with-unit-tests/
Global Error Handling in .NET Just Got WAY Better - YouTube, diakses Agustus 13, 2025, https://www.youtube.com/watch?v=rXdsm9R5TR0
Handling Errors with IExceptionHandler in ASP.NET Core 8.0 | by ..., diakses Agustus 13, 2025, https://medium.com/@AntonAntonov88/handling-errors-with-iexceptionhandler-in-asp-net-core-8-0-48c71654cc2e
Global Error Handling in ASP.NET Core: From Middleware to Modern Handlers, diakses Agustus 13, 2025, https://www.milanjovanovic.tech/blog/global-error-handling-in-aspnetcore-from-middleware-to-modern-handlers
Handle errors in ASP.NET Core | Microsoft Learn, diakses Agustus 13, 2025, https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling?view=aspnetcore-9.0
Error Handling in .NET Core Web API with Custom Middleware - C# Corner, diakses Agustus 13, 2025, https://www.c-sharpcorner.com/article/error-handling-in-net-core-web-api-with-custom-middleware/
