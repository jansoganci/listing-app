window.onload = function() {
    const categorySearch = document.getElementById('categorySearch');
    const categoryDropdown = document.getElementById('categoryDropdown');
    const uploadForm = document.getElementById('uploadForm'); // Form elementi
    let selectedCategory = ''; // Seçilen kategoriyi saklamak için bir değişken tanımlıyoruz

    // Kategori listesi
    const categories = {
        "Craft Supplies & Tools": ["Stickers", "Beads", "Sewing Supplies", "Knitting Patterns", "Embroidery Kits"],
        "Jewelry": ["Necklaces", "Earrings", "Bracelets", "Rings", "Anklets"],
        "Weddings": ["Invitations", "Thank You Cards", "Wedding Favors", "Guest Books", "Cake Toppers"],
        "Clothing": ["T-Shirts", "Hoodies", "Dresses", "Handmade Clothing", "Baby Clothing"],
        "Accessories": ["Hair Clips", "Scarves", "Sunglasses", "Baby Accessories", "Belts"],
        "Bath & Beauty Products": ["Bar Soaps", "Lotions", "Bath Bombs", "Face Masks", "Essential Oils"],
        "Home & Living": ["Home Decor", "Candles", "Furniture", "Kitchenware", "Wall Art"],
        "Paper & Party Supplies": ["Invitations", "Placeholders", "Party Banners", "Cake Toppers", "Printables"],
        "Art & Collectibles": ["Art Prints", "Sculptures", "Digital Art", "Posters", "Original Paintings"],
        "Vintage Items": ["Vintage Jewelry", "Vintage Clothing", "Vintage Furniture", "Vintage Memorabilia", "Vintage Accessories"],
        "Personalized Gifts": ["Custom Jewelry", "Custom Prints", "Personalized Mugs", "Engraved Items", "Custom Phone Cases"],
        "Zero-Waste Products": ["Reusable Bags", "Plant-Based Tools", "Cloth Towels", "Bar Soaps (Dish, Hair, Body)", "Bamboo Products"],
        "Pet Supplies": ["Custom Pet Collars", "Pet Clothing", "Pet Beds", "Pet Toys", "Leashes"],
        "Toys & Entertainment": ["Wooden Toys", "Educational Games", "Board Games", "Puzzles", "Stuffed Animals"],
        "Bags & Purses": ["Handmade Totes", "Backpacks", "Crossbody Bags", "Laptop Bags", "Clutches"],
        "Books": ["Fiction", "Non-fiction", "Art Books", "Children's Books", "Cookbooks", "Educational Books"],
        "Digital Content": ["E-book", "PDF Study Notes", "Digital Art Book"]
    };

    // Kategorileri dolduruyoruz
    for (const category in categories) {
        const categoryDiv = document.createElement('div');
        categoryDiv.textContent = category;
        categoryDiv.classList.add('category');
        categoryDropdown.appendChild(categoryDiv);

        const subcategories = categories[category];
        subcategories.forEach(subcategory => {
            const subcategoryDiv = document.createElement('div');
            subcategoryDiv.textContent = ' - ' + subcategory;
            subcategoryDiv.classList.add('subcategory');
            subcategoryDiv.onclick = function() {
                selectedCategory = category + ' > ' + subcategory; // Seçilen kategoriyi güncelliyoruz
                categorySearch.value = selectedCategory;
                categoryDropdown.style.display = 'none'; // Seçim sonrası dropdown'ı kapat
            };
            categoryDropdown.appendChild(subcategoryDiv);
        });
    }

    // Arama yaparken kategori dropdown'ını gösteriyoruz
    categorySearch.oninput = function() {
        const filter = categorySearch.value.toLowerCase();
        const categoryDivs = categoryDropdown.getElementsByTagName('div');
        Array.from(categoryDivs).forEach(div => {
            if (div.textContent.toLowerCase().includes(filter)) {
                div.style.display = '';
            } else {
                div.style.display = 'none';
            }
        });
        categoryDropdown.style.display = 'block'; // Arama sırasında dropdown'ı açık tut
    };

    // Sayfanın herhangi bir yerine tıklandığında dropdown'ı kapatıyoruz
    document.addEventListener('click', function(e) {
        if (!categorySearch.contains(e.target)) {
            categoryDropdown.style.display = 'none';
        }
    });

    // Form submit olayında kategori bilgisini formData'ya ekliyoruz
    uploadForm.onsubmit = async function(e) {
        e.preventDefault(); // Sayfanın yeniden yüklenmesini önlüyoruz

        const formData = new FormData(uploadForm);

        // Seçili kategoriyi formData'ya ekliyoruz
        if (selectedCategory) {
            formData.append('category', selectedCategory); // Seçilen kategori ekleniyor
        } else {
            alert("Please select a category.");
            return; // Kategori seçilmemişse formu göndermiyoruz
        }

        const titleDiv = document.getElementById("outputTitle");
        const descriptionDiv = document.getElementById("outputDescription");
        const altTextDiv = document.getElementById("outputAltText");
        const keywordsDiv = document.getElementById("outputKeywords");

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                const result = await response.json();

                // AI'den gelen başlık, açıklama, alt metin ve anahtar kelimeleri ekrana bas
                titleDiv.textContent = result.title || "Title not generated";
                descriptionDiv.textContent = result.description || "Description not generated";
                altTextDiv.textContent = result.alt_text || "Alt Text not generated";
                keywordsDiv.textContent = result.keywords || "Keywords not generated";
            } else {
                titleDiv.textContent = "Error: Unable to process the request.";
                descriptionDiv.textContent = "Error: Unable to process the request.";
                altTextDiv.textContent = "Error: Unable to process the request.";
                keywordsDiv.textContent = "Error: Unable to process the request.";
            }
        } catch (error) {
            console.error("Error:", error);
            titleDiv.textContent = "An error occurred while uploading the file.";
            descriptionDiv.textContent = "An error occurred while uploading the file.";
            altTextDiv.textContent = "An error occurred while uploading the file.";
            keywordsDiv.textContent = "An error occurred while uploading the file.";
        }
    };
};
