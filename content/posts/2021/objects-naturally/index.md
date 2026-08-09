---
title: Objects, Naturally
date: '2021-01-29T17:12:32+01:00'
slug: objects-naturally
layout: single
categories:
- Code
- Work
cover: cover-01-monitor-scene.jpg
postLang: en
aliases:
- /2021/01/29/objects-naturally/
wp_original: https://orlotech.netsons.org/2021/01/29/objects-naturally/
---

Also, is re-inventing the wheel always wrong?

This is a (hopefully short) story of something that happened to me while developing business applications over the last few years.

After developing a couple of them as part of a small team, I began to feel more and more how the whole thing was... put as pun... a redundancy of redundancies.

Everybody is using the same objects (models, poco, name them as you prefer) as Customer, Company, Product and so on. We used to spend a lot of time designing the Data Acquisition Layer, the Business Logic Layer, and the front-end (in my case, WPF and UWP). Of course the necessity of adopting MVVM was soon clear, but still everything was so boilerplate and repetitive. In every layer, every single object would spam around tenths if not hundreds line of code.

Personally, even having just 2 lines repeated 2 or 3 times is enough to start bothering me.

And what about the Views? Not only I would have very similar ViewModels laying around, but also a whole lot of XAML pages with the proper controls bound to the matching properties of the object in discussion, like:

```
<TextBox Text="{Binding TextProperty}"/>
```

It soon started to occur to me that the major obstacle was to be able to both have the controls built at runtime AND have the Views be somehow dynamically generated as well.

All these feelings were being reinforced as well looking at websites like https://schema.org/ - everything is an object, and every complex object is the result of the composition of simpler ones. This should be obvious: Customer and a Employee are after all two different "specialization" of a Person. A significant part of their nature is shared. You don't want to describe it twice. No, you really should not.

Few months ago, an opportunity to implement some of the swarms of principles nesting in my head arose when my friends wanted to develop a customizable, extensible business application which needed to be a code base to easily customize according to each single specific customer profile (a construction company, a wine seller, a medical office, to start with, and so on).

This led to the planning and developing of what has proved to be my first framework. There's much to improve, but I allow myself to feel satisfaction from achieving a first milestone on the road to Software Architect.

It has been carried out in the name of generics. And reflection. Ironically, lot of reflection (on my side) led to a lot of reflection (in the code).

Models share a common interface (or base class) and make use of a number of attributes to specify behaviors around the single properties, helped by few naming convention (yes, you want to use a wiki to document your project and share information with your team); API receives requests and polls the Database. The whole DAL is around 1k lines of code, doing mapping ([ListHelper](https://www.codeproject.com/articles/1009908/generic-listhelper-class-net)) with a single series of CRUD methods (recursive, by the way, if you need to fill the dependencies of the objects). The objects are tables in the DBs and a series of views spanning across them forming the specialized, inheriting objects.

Model:

```
[ClassInfo(SQLName = "companies")]
public class Company : Anagraphic
{
[ValueInfo(SQLName = "legalName")]
public string LegalName { get; set; }
...
```

Database select anything:

```
 public List<T> SelectObjects<T>(int? idToMatch = null, string tableAttritbute = null, string idName = null)
        {
            try
            {
                var classInfo = typeof(T).GetCustomAttribute(typeof(ClassInfo)) as ClassInfo;

                if (classInfo != null)
                {
                    if (tableAttritbute == null)
                        tableAttritbute = classInfo.SQLName;

                    string query = "SELECT * FROM " + tableAttritbute;

                    if (idToMatch.HasValue)
                    {
                        query += $" WHERE id{idName} = {idToMatch}";
                    }

                    var results = new ListHelperV1<T>(ConnectionString).GetData(query);

                    FillDependenciesExperimental(results);
                    return results;

                }
                return null;
            }
        }
```

Now, this is accessed via REST API (async bla bla bla) from the application. Now here's a treat: I managed to build a library (UWP) of both ViewModels (extending) AND Views (dynamically populated AND **bound at runtime**).\
Underlying all of them, the base crud ViewModel:

```
public class BaseCrudVM : SingleTabVM
{
     public BaseCrudVM()
     {
          CreateItem = new RelayCommand(CreateItemCommand);
          DeleteItem = new RelayCommand(DeleteItemCommand);
          UpdateItem = new RelayCommand(UpdateItemCommand);
          EditItem = new RelayCommand(EditItemCommand);
          RefreshItems = new RelayCommand(RefreshItemsCommand);
     ...
```

Each inheriting VM (a different one for each View archetype) populates a FrameworkElement property (bound to the dynamic element in the View) with the controls coming from the type of the object and from its properties' types and attributes.

```
if (valueInfo.IsVisible)
{
    if(renderInfo.IsFixedValue)
    {
        controls.Add(CreateComboBox(property));
    }
    else if (type == typeof(Boolean))
    {
        controls.Add(CreateToggleSwitch(property));
    }
    else if (type == typeof(DateTime))
    {
        if (property.Name == "Created" || property.Name == "LastModify")
            controls.Add(CreateDateTextBox(property));
        else
            controls.Add(CreateDatePicker(property));
    }
}
```

Which calls methods like:

```
TextBox CreateTextBox(PropertyInfo property)
{
    var tb = new TextBox { Style = (Style)Application.Current.Resources["BaseTextBox"] };
    Binding bindingText = new Binding { Path = new PropertyPath($"SelectedItem.{property.Name}") };

    if (property.DeclaringType.Name == "BaseModel")
    {
        bindingText.Mode = BindingMode.OneWay;
        bindingText.UpdateSourceTrigger = UpdateSourceTrigger.PropertyChanged;
        tb.IsReadOnly = true;
    }
    return tb;
}
```

Once these components were all completed and tested, the single final applications were very easily produced and customized: trivial things like adding a table and a view to the db, extending both an existing model as well as an existing VM, reinjecting it into the View.....\
The whole thing is presented using a TabView for the content inside of a NavigationView to navigate the different objects. The left side menu is populated with something like this:

```
List TreeViewList = new List
{
    new MenuNode()
    {
        Name = resourceLoader.GetString("customers"),
        Glyph = Symbol.Contact,
        ViewType = typeof(UI.Tabs.ListDetail.ListDetail),
        ViewModelType = typeof(UI.Tabs.ListDetail.ListDetailVM)
    }
...
```

The resulting feeling is that of a spontaneous flourishing of a GUI from an object, as if its nature is naturally manifesting itself through the code.

If nothing else, you now know how I love languages and puns :D

---

Some time later, I discover Naked Objects Framework, finding out that I was re-discovering some of the same principles. To me, it sounded like the confirmation of having chosen the right path.\
<https://en.wikipedia.org/wiki/Naked_objects>\
<https://en.wikipedia.org/wiki/Object-oriented_user_interface>

(If you want more information about the project, write to [info@teksistemi.com](mailto:info@teksistemi.com))
