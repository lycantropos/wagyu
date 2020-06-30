#include <pybind11/operators.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <mapbox/geometry/point.hpp>
#include <sstream>

namespace py = pybind11;

#define MODULE_NAME _wagyu
#define C_STR_HELPER(a) #a
#define C_STR(a) C_STR_HELPER(a)
#define POINT_NAME "Point"

using coordinate_t = double;
using Point = mapbox::geometry::point<coordinate_t>;

static std::ostringstream make_stream() {
  std::ostringstream stream;
  stream.precision(std::numeric_limits<coordinate_t>::digits10 + 2);
  return stream;
}

static std::string point_repr(const Point& self) {
  auto stream = make_stream();
  stream << C_STR(MODULE_NAME) "." POINT_NAME "(" << self.x << ", " << self.y
         << ")";
  return stream.str();
}

static std::string bool_repr(bool value) { return py::str(py::bool_(value)); }

PYBIND11_MODULE(MODULE_NAME, m) {
  m.doc() = R"pbdoc(
        Python binding of mapbox/wagyu library.
    )pbdoc";

  py::class_<Point>(m, POINT_NAME)
      .def(py::init<coordinate_t, coordinate_t>(), py::arg("x"), py::arg("y"))
      .def(py::pickle(
          [](const Point& self) {  // __getstate__
            return py::make_tuple(self.x, self.y);
          },
          [](py::tuple tuple) {  // __setstate__
            if (tuple.size() != 2) throw std::runtime_error("Invalid state!");
            return Point(tuple[0].cast<coordinate_t>(),
                         tuple[1].cast<coordinate_t>());
          }))
      .def(py::self == py::self)
      .def("__repr__", point_repr)
      .def_readonly("x", &Point::x)
      .def_readonly("y", &Point::y);

#ifdef VERSION_INFO
  m.attr("__version__") = VERSION_INFO;
#else
  m.attr("__version__") = "dev";
#endif
}
